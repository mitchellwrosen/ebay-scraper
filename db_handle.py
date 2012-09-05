from logging import *
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
  def RegisterDatabaseTableListener(self, listener, table):
    if table in self.table_listeners:
      self.table_listeners[table].append(listener)
    else:
      self.table_listeners[table] = [listener]

  def Select(self, columns, table, cond=None):
    self.lock.acquire()

    statement = 'SELECT %s FROM %s' % (', '.join(columns), table)
    if cond is not None:
      statement += ' WHERE %s' % cond

    LOG(INFO, statement)
    self.cursor.execute(statement)
    results = self.cursor.fetchall()

    self.lock.release()
    return results

  def Insert(self, table, columns, values):
    self.lock.acquire()

    statement = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(columns),
        ', '.join([str(value) for value in values]))

    LOG(INFO, statement)
    self.cursor.execute(statement)
    affected = self.cursor.rowcount

    if table in self.table_listeners:
      for listener in self.table_listeners[table]:
        threading.Thread(target=listener.OnInsert,
                         args=(table, columns, values),
                         name='OnInsert_%s' % table).start()

    self.lock.release()
    return affected

class PhoneDatabaseHandle(DatabaseHandle):
  def __init__(self, database_info):
    super(PhoneDatabaseHandle, self).__init__(database_info)

  '''
  Gets the id of a phone. Inserts a new entry into the database if necessary.
  '''
  def GetId(self, phone):
    id = self.Select(
        ['id'],
        'phone',
        ('model="%s" AND brand="%s" AND storage_capacity="%s" AND '
         'carrier="%s" AND cond="%s"') % (phone.model, phone.brand,
                                          phone.storage_capacity, phone.carrier,
                                          phone.cond))

    if not id:
      self.InsertPhone(phone)

      id = self.Select(
          ['id'],
          'phone',
          ('model="%s" AND brand="%s" AND storage_capacity="%s" AND '
           'carrier="%s" AND cond="%s"') % (phone.model, phone.brand,
                                            phone.storage_capacity,
                                            phone.carrier, phone.cond))

    return id[0][0]

  def InsertPhone(self, phone):
    columns = ('model', 'brand', 'cond')
    values = ("'%s'" % phone.model, "'%s'" & phone.brand, "'%s'" & phone.cond)

    if phone.storage_capacity:
      columns += ('storage_capacity',)
      values += ("'%s'" % phone.storage_capacity,)

    for optional in ['storage_capacity', 'carrier', 'color']:
      val = getattr(phone, optional)
      if val:
        columns += (optional,)
        values += ("'%s'" % val,)

    self.Insert('phone', columns, values)

  '''
  Gets the most recent average sale price of a phone with id |id|.
  '''
  def GetAverageSale(self, id):
    average_sale = self.Select(
        ['price'],
        'averagesale',
        'timestamp=(SELECT MAX(timestamp) FROM averagesale WHERE id=%s)' % id)
    if not average_sale:
      return -1

    return average_sale[0][0]

  '''
  Inserts a new average sale of phone with id |id|, by averaging the last month
  of sales.
  '''
  def InsertAverageSale(self, id):
    # Grab the last month of sales
    sales = self.Select(['price'],
                        'sale',
                        'id=%s AND DATEDIFF(date, CURDATE()) <= 30' % (id))

    if not sales:
      return False

    average_sale = util.Average(util.Trim(sales, config.kTrimPercentage))
    self.Insert('averagesale', ('id', 'price'), (id, average_sale))

    return True

  '''
  Inserts a new sale into the database.
  '''
  def InsertSale(self, id, price):
    self.Insert('sale',
                ('id', 'price', 'date'),
                (id, price, 'CURDATE()'))

  def GetAllIds(self):
    all_ids = self.Select(['id'], 'phone')
    return [id for (id,) in all_ids]
