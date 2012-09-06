import average_sale_updater
import config
import db_handle
import scraper

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

  scrapers = []
  for phone in config.kPhones:
    ended_scraper = scraper.PhoneEndedScraper(db_handle,
                                              copy.deepcopy(config.kUrlInfo),
                                              phone,
                                              repeat_every=30)
    threading.Thread(target=ended_scraper.Run,
                     name='%s-ended' % phone.ToString()).start()
    time.sleep(1)

    bin_scraper = scraper.PhoneBINScraper(db_handle,
                                          copy.deepcopy(config.kUrlInfo),
                                          phone)
    threading.Thread(target=bin_scraper.Run,
                     name='%s-BIN' % phone.ToString()).start()
    time.sleep(1)

  # Spawn a thread to update averagesale periodically.
  #average_sale_updater = average_sale_updater.AverageSaleUpdater(db_handle)
  #threading.Thread(target=average_sale_updater.Run,
  #                 kwargs={'repeat_every': 60},
  #                 name='Average_Sale_Updater').start()
