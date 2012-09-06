import config
import db_handle
import ebay_constants
import util
from logging import *

import abc
import feedparser
import threading
import time
import urllib2

class Scraper(object):
  __metaclass__ = abc.ABCMeta

  def __init__(self, db_handle, url_info, repeat_every=60):
    self.db_handle = db_handle
    self.url_info = url_info
    self.latest = None

    self.name = None
    self.repeat_every = repeat_every
    self.running = False

  def FeedEntries(self):
    feed = feedparser.parse(urllib2.urlopen(self.request))
    self.old_latest = feed['entries'][0][self.latest_key]
    for entry in feed['entries']:
      yield entry

  def Run(self):
    if not self.name:
      self.name = threading.current_thread().name
    LOG(INFO, '%s: Running.' % self.name)
    self.running = True
    while True:
      if not self.Scrape():
        LOG(INFO, '%s: Stopping.' % self.name)
        self.running = False
        break
      util.Sleep(self.repeat_every)

  @abc.abstractmethod
  def Scrape(self):
    return

class PhoneScraper(Scraper):
  __metaclass__ = abc.ABCMeta

  def __init__(self, db_handle, url_info, phone, repeat_every=60):
    Scraper.__init__(self, db_handle, url_info, repeat_every=repeat_every)

    self.phone = phone
    self.id = self.db_handle.GetId(self.phone)

    # Augment url_info['get_params']
    self.url_info['get_params']['_dmpt'] = 'Cell_Phones'
    self.url_info['get_params']['_rss'] = '1'
    self.url_info['get_params']['rt'] = 'nc'
    self.url_info['get_params'][ebay_constants.kGETKeyCategory] = (
        ebay_constants.kGETValueCategoryCellPhonesAndSmartphones)
    self.url_info['get_params']['Brand'] = phone.brand
    self.url_info['get_params']['Storage Capacity'] = phone.storage_capacity
    self.url_info['get_params']['Carrier'] = phone.carrier
    self.url_info['get_params'][ebay_constants.kGETKeyItemCondition] = (
        phone.ebay_cond)

  '''
  Do work. Retun true to continue doing work, false to stop.
  '''
  @abc.abstractmethod
  def Scrape(self):
    return

class PhoneBINScraper(PhoneScraper):
  def __init__(self, db_handle, url_info, phone, repeat_every=30):
    PhoneScraper.__init__(self, db_handle, url_info, phone,
                          repeat_every=repeat_every)

    self.latest = time.gmtime()
    self.latest_key = 'updated_parsed'

    self.average_sale = -1

    # Augment url_info['get_params'] and intialize request.
    self.url_info['get_params'][ebay_constants.kGETKeyBIN] = '1'
    self.url_info['get_params'][ebay_constants.kGETKeySortByTimeNewlyListed] = (
        ebay_constants.kGETValueSortByTimeNewlyListed)
    self.request = util.GenerateRequest(self.url_info, self.phone.model)

    self.db_handle.RegisterDatabaseTableListener(self, 'averagesale')

  # DatabaseHandle.DatabaseTableListener implementation.
  def OnInsert(self, table, columns, values):
    if columns[0] == 'id' and values[0] == self.id:
      self.average_sale = self.db_handle.GetAverageSale(self.id)
      LOG(INFO, '%s: Updating average sale to %s' % (self.name,
                                                     self.average_sale))
      if not self.running and self.average_sale != -1:
        self.Run()

  def Scrape(self):
    LOG(INFO, '%s: Scraping %s' % (self.name, self.request.get_full_url()))
    if self.average_sale == -1:
      LOG(INFO, '%s: No average sale found (id %s).' % (self.name, self.id))
      return False

    for entry in self.FeedEntries():
      if (entry[self.latest_key] > self.latest):
        LOG(INFO, '%s: %s updated on %s for %s' % (
            self.name,
            entry['title'],
            entry['updated'],
            entry[ebay_constants.kRSSKeyBuyItNowPrice]))

    self.latest = self.old_latest

    return True

class PhoneEndedScraper(PhoneScraper):
  def __init__(self, cursor, url_info, phone, repeat_every=300):
    PhoneScraper.__init__(self, cursor, url_info, phone,
                          repeat_every=repeat_every)

    self.latest = int(time.time())
    self.latest_key = ebay_constants.kRSSKeyEndTime

    # Augment url_info['get_params'] and initialize request.
    self.url_info['get_params'][ebay_constants.kGETKeyCompleted] = '1'
    #self.url_info['get_params'][ebay_constants.kGETKeySold] = '1'
    self.request = util.GenerateRequest(self.url_info, self.phone.model)

  def Scrape(self):
    LOG(INFO, '%s: scraping %s' % (self.name, self.request.get_full_url()))

    for entry in self.FeedEntries():
      # eBay does milliseconds since epoch, so shave off the last 3 chars.
      if (int(entry[self.latest_key][:-3]) > self.latest and
          int(entry[ebay_constants.kRSSKeyBidCount]) > 0):
        LOG(INFO, '%s: %s %s (%s) sold for $%s on %s (%s bids)' % (
            self.name,
            self.phone.brand,
            self.phone.model,
            self.phone.cond,
            float(entry[ebay_constants.kRSSKeyCurrentPrice]) / 100.00,
            util.EbayTimeToString(entry[ebay_constants.kRSSKeyEndTime]),
            entry[ebay_constants.kRSSKeyBidCount]))

        self.db_handle.InsertSale(
            self.id,
            float(entry[ebay_constants.kRSSKeyCurrentPrice]) / 100.00)

    self.latest = int(self.old_latest)

    return True
