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


  scrapers = [
    {
      'type': 'ended',
      'class': scraper.PhoneEndedScraper,
      'list': [],
    },
    #{
    #  'type': 'ending',
    #  'class': scraper.PhoneEndingScraper,
    #  'list': [],
    #},
    {
      'type': 'bin',
      'class': scraper.PhoneBINScraper,
      'list': [],
    }
  ]
  threads = []

  for phone in config.kPhones:
    for scraper in scrapers:
      new_scraper = scraper['class'](db_handle,
                                     copy.deepcopy(config.kUrlInfo),
                                     phone)

      scraper['list'].append(new_scraper)
      threads.append(threading.Thread(target=new_scraper.Run,
                                      name='%s-%s' % (phone.ToString(),
                                                      scraper['type'])))

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
