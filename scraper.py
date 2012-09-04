import config
import db_util
import ebay_constants
import util
from logging import *

import abc
import feedparser
import threading
import time
import urllib
import urllib2

class Scraper(object):
  __metaclass__ = abc.ABCMeta

  def __init__(self, db_handle, url_info, repeat_every=60):
    self.db_handle = db_handle
    self.url_info = url_info
    self.latest = None
    self.repeat_every = repeat_every
    self.running = False

  def ParseFeed(self):
    feed = feedparser.parse(urllib2.urlopen(self.request))
    self.old_latest = feed['entries'][0][self.latest_key]
    for entry in feed['entries']:
      yield entry

  def Run(self):
    LOG('Thread begun.')
    self.running = True
    while True:
      if not self.Scrape():
        self.running = False
        break
      time.sleep(self.repeat_every)

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
    self.url_info['get_params']['_sacat'] = '9355'
    self.url_info['get_params']['_nkw'] = phone[0]
    self.url_info['get_params']['Brand'] = phone[1]
    self.url_info['get_params']['Storage Capacity'] = phone[2]
    self.url_info['get_params']['Carrier'] = phone[3]
    self.url_info['get_params']['LH_ItemCondition'] = (
        util.EbayItemCondition(phone[4]))

  @abc.abstractmethod
  def Scrape(self):
    return

class PhoneBINScraper(PhoneScraper):
  def __init__(self, db_handle, url_info, phone, repeat_every=60):
    PhoneScraper.__init__(self, db_handle, url_info, phone,
                          repeat_every=repeat_every)

    self.latest_key = 'published_parsed'

    # Augment url_info['get_params']
    self.url_info['get_params']['LH_BIN'] = '1'
    self.url_info['get_params']['_sop'] = '10'  # Sort by: Time: newly listed

    self.request = util.GenerateRequest(self.url_info)

    self.db_handle.RegisterDatabaseTableListener(self, 'averagesale')

    self.average_sale = -1
    self.update_average_sale_thread = (
        threading.Thread(target=self.UpdateAverageSale,
                         kwargs={'repeat_every' : 15}))
    self.update_average_sale_thread.start()

  # DatabaseHandle.DatabaseTableListener implementation.
  def OnInsert(self, table, columns, values):
    LOG('PhoneBINSScraper.OnInsert !!!')
    if columns[0] == 'id' and values[0] == self.id:
      self.average_sale = self.db_handle.GetAverageSale(self.id)
      LOG('Updating average sale - now %s' % self.average_sale)
      if not self.running and self.average_sale != -1:
        LOG('PhoneBINScraper running again.')
        self.Run()

  '''
  Periodically update self.average_sale. repeat_every should match the update
  frequency of the InsertAverageSale thread.
  '''
  def UpdateAverageSale(self, repeat_every=86400):
    while True:
      self.average_sale = self.db_handle.GetAverageSale(self.id)
      LOG('Updating average sale - now %s' % self.average_sale)
      if not self.running and self.average_sale != -1:
        LOG('PhoneBINScraper running again.')
        self.Run()
      time.sleep(repeat_every)

  def Scrape(self):
    LOG('PhoneBINScraper - scraping %s' % self.request.get_full_url())
    if self.average_sale == -1:
      LOG('No average sale found for %s %s (id %d). Stopping execution.' % (
          self.phone[config.kPhoneIndexBrand],
          self.phone[config.kPhoneIndexModel],
          self.id))
      return False

    for entry in self.ParseFeed():
      if (self.latest is None or
          entry[self.latest_key] > self.latest):
        LOG('%s posted on %s for %s' % (
            entry['title'],
            entry['published'],
            entry[ebay_constants.kKeyBuyItNowPrice]))

      self.latest = self.old_latest

    return True

class PhoneEndedScraper(PhoneScraper):
  def __init__(self, cursor, url_info, phone, repeat_every=60):
    PhoneScraper.__init__(self, cursor, url_info, phone,
                          repeat_every=repeat_every)

    self.latest_key = ebay_constants.kKeyEndTime

    # Augment url_info['get_params']
    self.url_info['get_params']['LH_Complete'] = '1'

    self.InitializeRequest()

  def Scrape(self):
    LOG('PhoneEndedScraper - scraping %s' % self.request.get_full_url())

    for entry in self.ParseFeed():
      if (self.latest is None or
          entry[self.latest_key] > self.latest):
        if int(entry[ebay_constants.kKeyBidCount]) > 0:
          LOG('%s sold for $%s on %s (%s bids)' % (
              entry['title'],
              float(entry[ebay_constants.kKeyCurrentPrice]) / 100.00,
              entry[ebay_constants.kKeyEndTime],
              entry[ebay_constants.kKeyBidCount]))

          db_util.InsertSale(
              self.cursor,
              self.id,
              float(entry[ebay_constants.kKeyCurrentPrice]) / 100.00)

    self.latest = self.old_latest

    return True
