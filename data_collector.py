import config
import db_util
import ebay_constants
import util
from logging import *

import abc
import MySQLdb as mdb
import sys
import threading
import time
import urllib
import urllib2
import feedparser
from HTMLParser import HTMLParser 
  
class Scraper(object, threading.Thread):
  __metaclass__ = abc.ABCMeta

  def __init__(self, cursor, url_info, repeat_every=60):
    threading.Thread.__init__(self)
    
    self.cursor = cursor
    self.url_info = url_info
    self.latest = None
    self.repeat_every = repeat_every
    
  '''
  Initializes urllib2.Request object, to be called after url_info['get_params']
  is fully initialized.
  '''
  def InitializeRequest(self):
    encoded_get_params = urllib.urlencode(self.url_info['get_params'])
    self.request = urllib2.Request(
        self.url_info['base_url'] + encoded_get_params,
        '',
        self.url_info['headers'])
    LOG(self.request.get_full_url())

  def ParseFeed(self):
    feed = feedparser.parse(urllib2.urlopen(self.request))
    self.old_latest = feed['entries'][0][self.latest_key]
    for entry in feed['entries']:
      yield entry
  
  def run(self):
    while True:
      self.Scrape()
      time.sleep(self.repeat_every)
  
  @abc.abstractmethod
  def Scrape(self):
    return

class PhoneScraper(Scraper):
  __metaclass__ = abc.ABCMeta

  def __init__(self, cursor, url_info, phone, repeat_every=60):
    Scraper.__init__(self, cursor, url_info, repeat_every=repeat_every)
   
    self.phone = phone
    self.id = db_util.GetId(self.cursor, self.phone)
    
    # Augment url_info['get_params']
    self.url_info['get_params']['_dmpt'] = 'Cell_Phones'
    self.url_info['get_params']['_rss'] = '1'
    self.url_info['get_params']['rt'] = 'nc'
    self.url_info['get_params']['_sacat'] = '9355'
    self.url_info['get_params']['_nkw'] = phone[0]
    self.url_info['get_params']['Brand'] = phone[1]
    self.url_info['get_params']['Storage Capacity'] = phone[2]
    self.url_info['get_params']['Carrier'] = phone[3]
    self.url_info['get_params']['LH_ItemCondition'] = util.EbayItemCondition(phone[4])

  @abc.abstractmethod
  def Scrape(self):
    return
      
class PhoneBINScraper(PhoneScraper):
  def __init__(self, cursor, url_info, phone, repeat_every=60):
    PhoneScraper.__init__(self, cursor, url_info, phone, 
                          repeat_every=repeat_every)
    
    self.latest_key = 'published_parsed'
    
    # Augment url_info['get_params']
    self.url_info['get_params']['LH_BIN'] = '1'
    self.url_info['get_params']['_sop'] = '10'  # Sort by: Time: newly listed
    
    # Initialize request
    self.InitializeRequest()

    self.avg_sale = db_util.GetAverageSale(self.cursor, self.id)    

  def Scrape(self):
    if self.avg_sale == -1:
      LOG('No average sale found for %s %s (id %d).' % (
          self.phone[config.kPhoneIndexBrand], 
          self.phone[config.kPhoneIndexModel], 
          self.id))
      return
  
    for entry in self.ParseFeed():
      if (self.latest is None or
          entry[self.latest_key] > self.latest):
        LOG('%s posted on %s for %s' % (
            entry['title'],
            entry['published'],
            entry[ebay_constants.kKeyBuyItNowPrice]))
      
      self.latest = self.old_latest
      
class PhoneEndedScraper(PhoneScraper):
  def __init__(self, cursor, url_info, phone, repeat_every=60):
    PhoneScraper.__init__(self, cursor, url_info, phone, 
                          repeat_every=repeat_every)

    self.latest_key = ebay_constants.kKeyEndTime
    
    # Augment url_info['get_params']
    self.url_info['get_params']['LH_Complete'] = '1'
    
    self.InitializeRequest()
  
  def Scrape(self):
    for entry in self.ParseFeed():
      if (self.latest is None or
          entry[self.latest_key] > self.latest):
        if int(entry[ebay_constants.kKeyBidCount]) > 0:
          LOG('%s sold for $%s on %s (%s bids)' % (
              entry['title'], 
              float(entry[ebay_constants.kKeyCurrentPrice]) / 100.00,
              entry[ebay_constants.kKeyEndTime], 
              entry[ebay_constants.kKeyBidCount]))
    
    self.latest = self.old_latest
        
      
################################################################################
if __name__ == '__main__':
  url_info = {
    'base_url' : config.kBaseUrl,
    'get_params' : {},
    'headers' : config.kHeaders,
  }
  
  con = mdb.connect(host=config.kDatabaseInfo['host'], 
                    user=config.kDatabaseInfo['user'],
                    passwd=config.kDatabaseInfo['passwd'], 
                    db=config.kDatabaseInfo['db'])
  
  with con:
    cursor = con.cursor()
    for phone in config.kPhones:
      bin_scraper = PhoneBINScraper(cursor, url_info, phone, repeat_every=10)
      bin_scraper.start()
      
      #ended_scraper = PhoneEndedScraper(cursor, url_info, phone)
      #ended_scraper.Run(repeat_every=5)