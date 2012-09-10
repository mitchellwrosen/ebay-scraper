import average_sale_updater
import config
import db_handle
import scraper
import util

import copy
import logging
import threading
import time

@util.safe
def main():
  handle = db_handle.PhoneDatabaseHandle(config.kDatabaseInfo)

  scrapers = [
    {
      'type': 'ended',
      'class': scraper.PhoneEndedScraper,
      'args': {
        'db_handle': handle,
        'url_info': copy.deepcopy(config.kUrlInfo),
        'tables': [],
      },
      'list': [],
    },
    {
      'type': 'bin',
      'class': scraper.PhoneBINScraper,
      'args': {
        'db_handle': handle,
        'url_info': copy.deepcopy(config.kUrlInfo),
        'tables': [],
      },
      'list': ['averagesale'],
    },
  ]
  threads = []

  # Spawn each type of scraper for each type of phone (1 thread each), 10
  # seconds apart so as to avoid too many open sockets when requesting URLs
  # (hackish solution, I know).
  for phone in config.kPhones:
    for scraper_template in scrapers:
      new_scraper = scraper_template['class'](
          scraper_template['db_handle'],
          scraper_template['url_info'],
          phone,
          scraper_template['tables'])
      scraper_template['list'].append(new_scraper)
      threads.append(
          threading.Thread(target=new_scraper.Run,
                           name='%s-%s' % (phone.ToString().replace(' ', '_'),
                                           scraper_template['type'])))

  for index in range(len(threads)):
    threads[index].start()
    logging.info('[%s/%s] threads launched.' % (index, len(threads)))
    time.sleep(10)

  # Spawn a thread to update averagesale periodically.
  average_sale_updater = average_sale_updater.AverageSaleUpdater(handle)
  threading.Thread(target=average_sale_updater.Run,
                   kwargs={'repeat_every': 60},
                   name='Average_Sale_Updater').start()

if __name__ == '__main__':
  main()
