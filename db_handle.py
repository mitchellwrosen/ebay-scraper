import util

import abc
import MySQLdb
import threading

class DatabaseHandle(object):
  '''
  Abstract base class to be extended by classes who wish to listen to database
  changes.
  '''
  class DatabaseTableListener(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, tables):
      for table in tables:
        self.db_handle.RegisterDatabaseTableListener(self, table)

    @abc.abstractmethod
    def OnInsert(self, table, column, values):
      return

  def __init__(self, database_info):
    self.conn = MySQLdb.connect(host=database_info['host'],
                                user=database_info['user'],
                                passwd=database_info['passwd'],
                                db=database_info['db'])
    self.cursor = self.conn.cursor()
    self.lock = threading.Semaphore()
    self.table_listeners = {}

  '''
  Register a class to listen to a particular table's changes.
  '''
  @util.safe
  def RegisterDatabaseTableListener(self, listener, table):
    if table in self.table_listeners:
      self.table_listeners[table].append(listener)
    else:
      self.table_listeners[table] = [listener]

  @util.safe
  def Select(self, columns, table, cond=None):
    self.lock.acquire()

    statement = 'SELECT %s FROM %s' % (', '.join(columns), table)
    if cond:
      statement += ' WHERE %s' % cond

    logging.info(statement)
    self.cursor.execute(statement)
    results = self.cursor.fetchall()

    self.lock.release()
    return results

  @util.safe
  def Insert(self, table, columns, values):
    self.lock.acquire()

    statement = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(columns),
        ', '.join([str(value) for value in values]))

    logging.info(statement)
    self.cursor.execute(statement)
    affected = self.cursor.rowcount

    if table in self.table_listeners:
      for listener in self.table_listeners[table]:
        threading.Thread(target=listener.OnInsert,
                         args=(table, columns, values),
                         name='OnInsert_%s' % table).start()

    self.lock.release()
    return affected

  @util.safe
  def Delete(self, table, cond=None):
    self.lock.acquire()

    statement = 'DELETE FROM %s' % table
    if cond:
      statement += ' WHERE %s' % cond

    logging.info(statement)
    self.cursor.execute(statement)
    affected = self.cursor.rowcount

    self.lock.release()
    return affected

class PhoneDatabaseHandle(DatabaseHandle):
  def __init__(self, database_info):
    super(PhoneDatabaseHandle, self).__init__(database_info)

  '''
  Gets the id of a phone. Inserts a new entry into the database if necessary.
  '''
  @util.safe
  def GetId(self, phone):
    cond = 'model="%s" AND brand="%s" AND cond="%s" AND carrier="%s"' % (
        phone.model, phone.brand, phone.cond, phone.carrier)
    for optional in ['storage_capacity', 'color']:
      if hasattr(phone, optional):
        cond += ' AND %s="%s"' % (optional, getattr(phone, optional))

    id = self.Select(['id'], 'phone', cond=cond)
    if not id:
      self.InsertPhone(phone)
      id = self.Select(['id'], 'phone', cond=cond)

    return id[0][0]

  @util.safe
  def InsertPhone(self, phone):
    columns = ('model', 'brand', 'cond', 'carrier')
    values = ("'%s'" % phone.model, "'%s'" % phone.brand, "'%s'" % phone.cond,
              "'%s'" % phone.carrier)

    for optional in ['storage_capacity', 'color']:
      if hasattr(phone, optional):
        columns += (optional,)
        values += ("'%s'" % getattr(phone, optional),)

    self.Insert('phone', columns, values)

  '''
  Gets the most recent average sale price of a phone with id |id|.
  '''
  @util.safe
  def GetAverageSale(self, id):
    average_sale = self.Select(
        ['price'],
        'averagesale',
        cond='timestamp=(SELECT MAX(timestamp) FROM averagesale WHERE id=%s)' %
            id)
    if not average_sale:
      return -1

    return average_sale[0][0]

  '''
  Inserts a new average sale of phone with id |id|, by averaging the last month
  of sales.
  '''
  @util.safe
  def InsertAverageSale(self, id):
    # Grab the last month of sales
    sales = self.Select(['price'],
                        'sale',
                        cond='id=%s AND DATEDIFF(date, CURDATE()) <= 30' % (id))

    if not sales:
      return False

    average_sale = util.Average(util.Trim(sales, config.kTrimPercentage))
    self.Insert('averagesale', ('id', 'price'), (id, average_sale))

    return True

  '''
  Purges the database of all sales less than 10% of the phone's average sale.
  '''
  @util.safe
  def TrimSales(self, id, pct=.10):
    average_sale = self.GetAverageSale(id)
    if average_sale == -1:
      return

    self.Delete('sale', cond='price < %s * %s' % (average_sale, pct))

  '''
  Inserts a new sale into the database.
  '''
  @util.safe
  def InsertSale(self, id, price):
    self.Insert('sale',
                ('id', 'price', 'date'),
                (id, price, 'CURDATE()'))

  @util.safe
  def GetAllIds(self):
    all_ids = self.Select(['id'], 'phone')
    return [id for (id,) in all_ids]
