import average_sale_updater
import config
import database_handle
import scraper
from config import logger

import copy
import threading
import time

'''
Decorator that surrounds the function in a try/catch block and logs any
thrown exceptions.
'''
def log_exceptions(func):
  def wrapper():
    try:
      func()
    except Exception, e:
      logger.exception(e)

  return wrapper

@log_exceptions
def main():
  db_handle = database_handle.PhoneDatabaseHandle(config.kDatabaseInfo)

  scrapers = [
    {
      'type': 'ended',
      'class': scraper.PhoneEndedScraper,
      'args': {
        'db_handle': db_handle,
        'url_info': copy.deepcopy(config.kUrlInfo),
        'tables': [],
      },
      'list': [],
    },
    {
      'type': 'bin',
      'class': scraper.PhoneBINScraper,
      'args': {
        'db_handle': db_handle,
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
          scraper_template['args']['db_handle'],
          scraper_template['args']['url_info'],
          phone,
          scraper_template['args']['tables'])
      scraper_template['list'].append(new_scraper)
      threads.append(
          threading.Thread(target=new_scraper.Run,
                           name='%s-%s' % (phone.ToString().replace(' ', '_'),
                                           scraper_template['type'])))

  for index in range(len(threads)):
    threads[index].start()
    logger.info('[%s/%s] threads launched.' % (index, len(threads)))
    time.sleep(10)

  # Spawn a thread to update averagesale periodically.
  average_sale_updater = average_sale_updater.AverageSaleUpdater(handle)
  threading.Thread(target=average_sale_updater.Run,
                   kwargs={'repeat_every': 60},
                   name='Average_Sale_Updater').start()

  logger.info('main ending')

if __name__ == '__main__':
  main()
