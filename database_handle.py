from logging import *

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
    self.cursor = conn.cursor()
    self.lock = threading.Semaphore()
    self.table_listeners = {}

  def __enter__(self):
    pass

  def __exit__(self):
    pass

  '''
  Register a class to listen to a particular table's changes.
  '''
  def RegisterDatabaseTableListener(self, listener, table):
    if table in table_listeners:
      table_listeners[table].append(listener)
    else:
      table_listeners[table] = [listener]

  def Select(self, columns, table, cond=None):
    self.lock.acquire()

    statement = 'SELECT %s FROM %s' % (', '.join(columns), table)
    if where is not None:
      statement += ' WHERE %s' % cond

    LOG(statement)
    self.cursor.execute(statement)
    results = self.cursor.fetchall()

    self.lock.release()
    return results

  def Insert(self, table, columns, values):
    self.lock.acquire()

    statement = 'INSERT INTO %s (%s) VALUES (%s)' % (table,
                                                     ', '.join(columns),
                                                     ', '.join(values))

    LOG(statement)
    self.cursor.execute(statement)
    affected = self.cursor.rowcount

    if table in self.table_listeners:
      for listener in self.table_listeners:
        listener.OnInsert(table, column, values)

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
        ('model="%s" AND brand="%s" AND size="%s" AND carrier="%s" AND '
         'cond="%s"') % (phone[0], phone[1], phone[2], phone[3], phone[4]))

    if not id:
      self.Insert('phone',
                  ('model', 'brand', 'size', 'carrier', 'cond'),
                  ('%s', '%s', '%s', '%s', '%s') %
                      phone[0], phone[1], phone[2], phone[3], phone[4])

      id = self.Select(
          ['id'],
          'phone',
          ('model="%s" AND brand="%s" AND size="%s" AND carrier="%s" AND '
           'cond="%s"') % (phone[0], phone[1], phone[2], phone[3], phone[4]))

    return id[0][0]

  '''
  Gets the most recent average sale price of a phone with id |id|.
  '''
  def GetAverageSale(self, id):
    average_sale = self.Select(
        'price',
        'averagesale',
        'timestamp=(SELECT MAX(timestamp) FROM averagesale WHERE id=%s)' % id)
    if not average_sale
      return -1

    return average_sale[0][0]

  '''
  Inserts a new average sale of phone with id |id|, by averaging the last month
  of sales.
  '''
  def InsertAverageSale(self, id):
    seconds = 30 * 24 * 60 * 60

    # Grab the last month of sales
    sales = self.Select('price',
                        'sale',
                        'id=%s AND timestamp >= NOW() - %s' % (id, seconds))

    if not sales:
      return False

    average_sale = util.Average(util.Trim(sales, config.kTrimPercentage)
    self.Insert('averagesale', ('id', 'price'), (id, average_sale))

    return True

  '''
  Inserts a new sale into the database.
  '''
  def InsertSale(self, id, price):
    self.Insert('sale', ('id', 'price'), (id, price))
