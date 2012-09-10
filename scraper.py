import config
import db_handle
import ebay_constants
import email
import util

import abc
import feedparser
import logging
import threading
import time
import urllib2

class Scraper(object):
  __metaclass__ = abc.ABCMeta

  def __init__(self, db_handle, url_info, tables, repeat_every=60):
    self.db_handle = db_handle
    DatabaseHandle.DatabaseTableListener.__init__(self, tables)

    self.url_info = url_info
    self.latest = None

    self.name = None
    self.repeat_every = repeat_every
    self.running = False

  @util.safe
  def Run(self):
    if not self.name:
      self.name = threading.current_thread().name
    logging.info('%s: Running.' % self.name)
    self.running = True
    while True:
      if not self.Scrape():
        logging.info('%s: Stopping.' % self.name)
        self.running = False
        break
      util.Sleep(self.repeat_every)

  @abc.abstractmethod
  def Scrape(self):
    return

class PhoneScraper(Scraper):
  __metaclass__ = abc.ABCMeta

  def __init__(self, db_handle, url_info, phone, tables, repeat_every=60):
    Scraper.__init__(self, db_handle, url_info, tables,
                     repeat_every=repeat_every)

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

class PhoneEndedScraper(PhoneScraper):
  def __init__(self, cursor, url_info, phone, tables, repeat_every=3600):
    PhoneScraper.__init__(self, cursor, url_info, phone, tables,
                          repeat_every=repeat_every)

    self.latest = int(time.time())

    # Augment url_info['get_params'] and initialize request.
    self.url_info['get_params'][ebay_constants.kGETKeyCompleted] = '1'
    #self.url_info['get_params'][ebay_constants.kGETKeySold] = '1'
    self.request = util.GenerateRequest(self.url_info, self.phone.model)

  @util.safe
  def Scrape(self):
    logging.info('%s: scraping %s' % (self.name, self.request.get_full_url()))

    feed = feedparser.parse(urllib2.urlopen(self.request))
    for entry in feed['entries']:
      # eBay does milliseconds since epoch, so shave off the last 3 chars.
      if (int(entry[ebay_constants.kRSSKeyEndTime][:-3]) > self.latest and
          int(entry[ebay_constants.kRSSKeyBidCount]) > 0):
        logging.info('%s: %s %s (%s) sold for $%s on %s (%s bids)' % (
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

    self.latest = int(feed['entries'][0][ebay_constants.kRSSKeyEndTime])

    return True

# TODO(mitchell): Finish this whole class.
class PhoneEndingScraper(PhoneScraper):
  def __init__(self, cursor, url_info, phone, tables, repeat_every=300):
    PhoneScraper.__init__(self, cursor, url_info, phone, tables,
                          repeat_every=repeat_every)

    #self.latest =

    # Augment url_info['get_params'] and initialize request.

  @util.safe
  def Scrape(self):
    logging.info('%s: scraping %s' % (self.name, self.request.get_full_url()))

    feed = feedparser.parse(urllib2.urlopen(self.request))
    for entry in feed['entries']:
      pass

class PhoneBINScraper(PhoneScraper):
  def __init__(self, db_handle, url_info, phone, tables, repeat_every=30):
    PhoneScraper.__init__(self, db_handle, url_info, phone,
                          repeat_every=repeat_every)

    self.latest = time.gmtime()

    self.average_sale = -1

    # Augment url_info['get_params'] and intialize request.
    self.url_info['get_params'][ebay_constants.kGETKeyBIN] = '1'
    self.url_info['get_params'][ebay_constants.kGETKeySortByTimeNewlyListed] = (
        ebay_constants.kGETValueSortByTimeNewlyListed)
    self.request = util.GenerateRequest(self.url_info, self.phone.model)

  # DatabaseHandle.DatabaseTableListener implementation.
  @util.safe
  def OnInsert(self, table, columns, values):
    if columns[0] == 'id' and values[0] == self.id:
      self.average_sale = self.db_handle.GetAverageSale(self.id)
      logging.info('%s: Updating average sale to %s' % (self.name,
                                                        self.average_sale))
      if not self.running and self.average_sale != -1:
        self.Run()

  @util.safe
  def Scrape(self):
    logging.info('%s: Scraping %s' % (self.name, self.request.get_full_url()))
    if self.average_sale == -1:
      logging.info('%s: No average sale found (id %s).' % (self.name, self.id))
      return False

    feed = feedparser.parse(urllib2.urlopen(self.request))
    for entry in feed['entries']:
      if (entry['updated_parsed'] > self.latest):
        logging.info('%s: %s updated on %s for %s' % (
            self.name,
            entry['title'],
            entry['updated'],
            entry[ebay_constants.kRSSKeyBuyItNowPrice]))

    self.latest = feed['entries'][0]['updated_parsed']

    return True
