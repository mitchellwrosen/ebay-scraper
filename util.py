import ebay_constants
from logging import *

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
Maps an ebay item condition to a GET parameter.
'''
def EbayItemCondition(cond):
  return {
    'Used' : ebay_constants.kConditionUsed,
    'New' : ebay_constants.kConditionNew,
  }[cond]

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
def EbayTimeToString(time):
  return time.strftime('%A %b-%d-%Y %H:%M:%S',
                       time.localtime(time / 1000))
