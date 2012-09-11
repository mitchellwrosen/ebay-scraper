import config
import database_handle
import ebay_constants
import email
import util
from config import logger

import abc
import copy
import feedparser
import threading
import time
import urllib2

class Scraper(threading.Thread,
              database_handle.DatabaseHandle.DatabaseTableListener):
  __metaclass__ = abc.ABCMeta

  def __init__(self, name, db_handle, url_info, scrape_every,
               listen_to_tables):
    threading.Thread.__init__(self, name=name)
    self.scrape_every = scrape_every

    self.db_handle = db_handle
    database_handle.DatabaseHandle.DatabaseTableListener.__init__(
        self,
        listen_to_tables)

    self.url_info = copy.deepcopy(url_info)
    self.latest = None

  @util.log_exceptions
  def run(self):
    logger.info('Running.')
    while True:
      if not self.Scrape():
        logger.info('Stopping.')
        break
      util.Sleep(self.scrape_every)

  '''
  Do work. Retun true to continue doing work, false to stop.
  '''
  @abc.abstractmethod
  def Scrape(self):
    return

  # TODO(mitchell): add abstract method here, see if derived derived breaks.

class PhoneScraper(Scraper):
  __metaclass__ = abc.ABCMeta

  def __init__(self, phone, *args):
    Scraper.__init__(self, *args)

    self.phone = phone
    self.id = self.db_handle.GetId(self.phone)

    # Augment url_info['get_params']
    self.url_info['get_params']['Brand'] = phone.brand
    self.url_info['get_params']['Storage Capacity'] = phone.storage_capacity
    self.url_info['get_params']['Carrier'] = phone.carrier
    self.url_info['get_params'][ebay_constants.kGETKeyItemCondition] = (
        phone.ebay_cond)

class PhoneEndedScraper(PhoneScraper):
  def __init__(self, *args):
    PhoneScraper.__init__(self, *(args + (3600, [])))
    self.name = self.name + '-ended'

    self.latest = int(time.time())

    # Augment url_info['get_params'] and initialize request.
    self.url_info['get_params'][ebay_constants.kGETKeyCompleted] = '1'
    #self.url_info['get_params'][ebay_constants.kGETKeySold] = '1'
    self.request = util.GenerateRequest(self.url_info, self.phone.model)

  # DatabaseHandle.DatabaseTableListener implementation.
  def OnInsert(self, table, columns, values):
    pass

  # Scraper implementation.
  def Scrape(self):
    logger.info('Scraping %s' % self.request.get_full_url())

    feed = feedparser.parse(urllib2.urlopen(self.request))
    for entry in feed['entries']:
      # eBay does milliseconds since epoch, so shave off the last 3 chars.
      if (int(entry[ebay_constants.kRSSKeyEndTime][:-3]) > self.latest and
          int(entry[ebay_constants.kRSSKeyBidCount]) > 0):
        logger.info('%s %s (%s) sold for $%s on %s (%s bids)' % (
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
  def __init__(self, *args):
    PhoneScraper.__init__(self, *(args + (300, [])))
    self.name = self.name + '-ending'

    #self.latest =

    # Augment url_info['get_params'] and initialize request.

  # DatabaseHandle.DatabaseTableListener implementation.
  def OnInsert(self, table, columns, values):
    pass

  # Scraper implementation.
  def Scrape(self):
    logger.info('Scraping %s' % self.request.get_full_url())

    feed = feedparser.parse(urllib2.urlopen(self.request))
    for entry in feed['entries']:
      pass

class PhoneBINScraper(PhoneScraper):
  def __init__(self, *args):
    PhoneScraper.__init__(self, *(args + (30, ['averagesale'])))
    self.name = self.name + '-bin'

    self.latest = time.gmtime()

    self.average_sale = -1

    # Augment url_info['get_params'] and intialize request.
    self.url_info['get_params'][ebay_constants.kGETKeyBIN] = '1'
    self.url_info['get_params'][ebay_constants.kGETKeySortByTimeNewlyListed] = (
        ebay_constants.kGETValueSortByTimeNewlyListed)
    self.request = util.GenerateRequest(self.url_info, self.phone.model)

  # DatabaseHandle.DatabaseTableListener implementation.
  def OnInsert(self, table, columns, values):
    if columns[0] == 'id' and values[0] == self.id:
      self.average_sale = self.db_handle.GetAverageSale(self.id)
      logger.info('Updating average sale to %s' % self.average_sale)
      if not self.is_alive() and self.average_sale != -1:
        self.run()

  # Scraper implementation.
  def Scrape(self):
    logger.info('Scraping %s' % self.request.get_full_url())
    if self.average_sale == -1:
      logger.info('No average sale found (id %s).' % self.id)
      return False

    feed = feedparser.parse(urllib2.urlopen(self.request))
    for entry in feed['entries']:
      if (entry['updated_parsed'] > self.latest):
        logger.info('%s updated on %s for %s' % (
            entry['title'],
            entry['updated'],
            entry[ebay_constants.kRSSKeyBuyItNowPrice]))

    self.latest = feed['entries'][0]['updated_parsed']

    return True
