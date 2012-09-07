import average_sale_updater
import config
import db_handle
import scraper
from logging import *

import copy
import threading
import time

if __name__ == '__main__':
  db_handle = db_handle.PhoneDatabaseHandle(config.kDatabaseInfo)

  # Initialize phones.
  for template in config.kPhoneTemplates:
    config.PopulatePhones(template['model'],
                          template['brand'],
                          template['conditions'],
                          template['carriers'],
                          template['storage_capacities'],
                          template['colors'])


  ended_scrapers = []
  bin_scrapers = []
  threads = []
  for phone in config.kPhones:
    ended_scrapers.append(
        scraper.PhoneEndedScraper(db_handle,
                                  copy.deepcopy(config.kUrlInfo),
                                  phone,
                                  repeat_every=30))

    bin_scrapers.append(
        scraper.PhoneBINScraper(db_handle,
                                copy.deepcopy(config.kUrlInfo),
                                phone))

  for scraper in ended_scrapers:
    threads.append(threading.Thread(target=scraper.Run,
                                    name='%s-ended' % phone.ToString()))

  for scraper in bin_scrapers:
    threads.append(threading.Thread(target=scraper.Run,
                                    name='%s-BIN' % phone.ToString()))

  i = 1
  for thread in threads:
    thread.start()
    LOG(INFO, '[%s/%s] threads launched.' % (i, len(threads)))
    i += 1
    time.sleep(10)

  # Spawn a thread to update averagesale periodically.
  average_sale_updater = average_sale_updater.AverageSaleUpdater(db_handle)
  threading.Thread(target=average_sale_updater.Run,
                   kwargs={'repeat_every': 60},
                   name='Average_Sale_Updater').start()
