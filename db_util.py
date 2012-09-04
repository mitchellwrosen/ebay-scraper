import util
from logging import *

import datetime
import sys
import threading

db_semaphore = threading.Semaphore()

'''
A simple cursor that logs each call to execute().
'''
class LoggingCursor(object):
  def __init__(self, cursor):
    self.cursor = cursor
    self.rowcount = cursor.rowcount

  def execute(self, arg):
    LOG(arg)
    self.cursor.execute(arg)
    self.rowcount = self.cursor.rowcount

  def fetchone(self):
    return self.cursor.fetchone()

  def fetchall(self):
    return self.cursor.fetchall()

'''
Gets the id of a phone. Inserts a new entry into the database if necessary.
'''
def GetId(cur, phone):
  db_semaphore.acquire()
  cur.execute("""
    SELECT id
    FROM phone
    WHERE model='{0}' AND brand='{1}' AND size='{2}' AND carrier='{3}' AND cond='{4}'
  """.format(phone[0], phone[1], phone[2], phone[3], phone[4]))
  id = cur.fetchone()
  if id is None:
    cur.execute("""
      INSERT INTO phone (model, brand, size, carrier, cond)
      VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')
    """.format(phone[0], phone[1], phone[2], phone[3], phone[4]))
    cur.execute("""
      SELECT id
      FROM phone
      WHERE model='{0}' AND brand='{1}' AND size='{2}' AND carrier='{3}' AND cond='{4}'
    """.format(phone[0], phone[1], phone[2], phone[3], phone[4]))
    ret = cur.fetchone()[0]
  else:
    ret = id[0]

  db_semaphore.release()
  return ret

'''
Gets the average sale price of a phone given its id.
'''
def GetAverageSale(cur, id):
  db_semaphore.acquire()
  cur.execute("""
    SELECT price
    FROM averagesale
    WHERE id={0}
  """.format(id))
  tup = cur.fetchone()
  if tup is not None:
    ret = tup[0]
  else:
    ret = -1

  db_semaphore.release()
  return ret

def UpdateAverageSale(cur, id):
  db_semaphore.acquire()
  cur.execute("""
    SELECT price
    FROM sale
    WHERE id={0}
  """.format(id))
  sales = cur.fetchall()
  if sales is None:
    db_semaphore.release()
    return -1

  avg_sale = util.Average(util.Trim(sales, .10))
  cur.execute("""
    UPDATE averagesale
    SET price={0}
    WHERE id={1}
  """.format(avg_sale, id))
  if cur.rowcount == 0:
    cur.execute("""
      INSERT INTO averagesale (id, price)
      VALUES ({0}, {1})
    """.format(id, avg_sale))
    ret = avg_sale
  elif cur.rowcount != 1:
    LOG('ERROR: More than one row in table "averagesale" have id %s' % id)
    ret = -1
  else:
    ret = avg_sale

  return ret

def InsertSale(cur, id, price):
  db_semaphore.acquire()
  cur.execute("""
    INSERT INTO sale (id, price)
    VALUES ({0}, {1})
  """.format(id, price))
  db_semaphore.release()
