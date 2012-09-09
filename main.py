import average_sale_updater
import config
import db_handle
import scraper

import copy
import logging
import threading
import time

def main():
  logging.basicConfig(level=config.kLoggingLevel)

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

  # Spawn each type of scraper for each type of phone (1 thread each), 10
  # seconds apart so as to avoid too many open sockets when requesting URLs.
  # (Hackish solution, I know).
  for phone in config.kPhones:
    for scraper in scrapers:
      new_scraper = scraper['class'](db_handle,
                                     copy.deepcopy(config.kUrlInfo),
                                     phone)

      scraper['list'].append(new_scraper)
      threads.append(
          threading.Thread(target=new_scraper.Run,
                           name='%s-%s' % (phone.ToString().replace(' ', '_'),
                                           scraper['type'])))

  for index in range(len(threads)):
    threads[index].start()
    logging.info('[%s/%s] threads launched.' % (index, len(threads)))
    time.sleep(10)

  # Spawn a thread to update averagesale periodically.
  average_sale_updater = average_sale_updater.AverageSaleUpdater(db_handle)
  threading.Thread(target=average_sale_updater.Run,
                   kwargs={'repeat_every': 60},
                   name='Average_Sale_Updater').start()

if __name__ == '__main__':
  main()

