import ebay_constants
from logging import *

import random
import time
import urllib
import urllib2

'''
Gets the average element in a list.
'''
def Average(list):
  if not list:
    return -1
  return sum(item[0] for item in list) / len(list)

'''
Trims |pct| percent (0-1) from either end of a list, and return the sorted list.
'''
def Trim(list, pct):
  chop_num = int(len(list) * pct)
  if chop_num == 0:
    return sorted(list)
  return sorted(list)[chop_num:-chop_num]

'''
Generates a urllib2.Request object from a url_info dictionary.
'''
def GenerateRequest(url_info):
  return urllib2.Request(
      url_info['base_url'] + urllib.urlencode(url_info['get_params']),
      '',
      url_info['headers'])

'''
Converts an "eBay time" (milliseconds since epoch) into a human-readable string.
'''
def EbayTimeToString(ebay_time):
  return time.strftime('%A %b-%d-%Y %H:%M:%S',
                       time.localtime(int(ebay_time) / 1000))

'''
Sleep with a random deviation to un-synchronize threads.
'''
def Sleep(secs):
  time.sleep(random.randrange(secs - 1, secs + 2))

