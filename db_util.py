import util
from logging import *

import datetime
import threading

db_semaphore = threading.Semaphore()
  
'''
Gets the id of a phone. Inserts a new entry into the database if necessary.
'''
def GetId(cur, phone):
  db_semaphore.acquire()
  cur.execute("SELECT id FROM phone WHERE model = '%s' and brand = '%s' and "
              "size = '%s' and carrier = '%s' and cond = '%s'" % (phone[0],
              phone[1], phone[2], phone[3], phone[4]))
  id = cur.fetchone()
  if id is None:
    LOG("INSERT INTO phone (model, brand, size, carrier, cond) "
                "VALUES ('%s', '%s', '%s', '%s', '%s')" % (phone[0], phone[1],
                phone[2], phone[3], phone[4]))
    cur.execute("INSERT INTO phone (model, brand, size, carrier, cond) "
                "VALUES ('%s', '%s', '%s', '%s', '%s')" % (phone[0], phone[1],
                phone[2], phone[3], phone[4]))
    cur.execute("SELECT id FROM phone WHERE model = '%s' and brand = '%s' and "
                "size = '%s' and carrier = '%s' and cond = '%s'" % (phone[0],
                phone[1], phone[2], phone[3], phone[4]))    
    ret = cur.fetchone()[0]
  else:
    ret = id[0]
  
  db_semaphore.release()
  return ret

'''
Gets the average sale price of a phone given its id. Queries the averagesale
table, updating it if necessary (more than 1 day old).
'''
def GetAverageSale(cur, id):
  db_semaphore.acquire()
  cur.execute("SELECT price, timestamp FROM averagesale WHERE id = %s" % id)
  tup = cur.fetchone()
  if tup is None:
    avg_sale = GetAverageSaleHelper(cur, id)
    cur.execute("INSERT INTO averagesale (id, price) VALUES (%s, %s)" % (
        id, avg_sale))
    ret = avg_sale
  elif (datetime.datetime.now() - tup[1]).days >= 1:
    avg_sale = GetAverageSaleHelper(cur, id)
    if (avg_sale != -1):
      cur.execute("DELETE FROM averagesale WHERE id = %s" % id)
      cur.execute("INSERT INTO averagesale (id, price) VALUES (%s, %s)" % (
          id, avg_sale))
    ret = avg_sale
  else:
    ret = tup[0]
  
  db_semaphore.release()
  return ret

'''
Gets the average sale price of a phone given its id, by querying the Sale table.
Returns -1 if there are no recorded sales of the phone.
'''
def GetAverageSaleHelper(cur, id):
  cur.execute("SELECT price FROM sale WHERE id = %s" % id)
  sales = cur.fetchall()
  if sales is None:
    return -1
  return util.Average(util.Trim(sales, .10))