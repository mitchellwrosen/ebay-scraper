import average_sale_updater
import config
import database_handle
import scraper
import util
from config import logger

import threading
import time

@util.log_exceptions
def main():
  db_handle = database_handle.PhoneDatabaseHandle(config.kDatabaseInfo)

  scraper_classes = [scraper.PhoneEndedScraper, scraper.PhoneBINScraper]

  # Spawn each type of scraper for each type of phone 5 seconds apart so as to
  # avoid too many open sockets when requesting URLs (hackish solution, I know).
  index = 1
  num_scrapers = len(config.kPhones) * len(scraper_classes)
  for phone in config.kPhones:
    for scraper_class in scraper_classes:
      scraper_class(phone,
                    phone.ToString().replace(' ', '_'),
                    db_handle,
                    config.kEbayPhoneUrlInfo).start()
      logger.info('[%s/%s] scrapers launched.' % (index, num_scrapers))
      index = index + 1
      time.sleep(5)

  # Spawn a thread to update averagesale periodically.
  average_sale_updater.AverageSaleUpdater('AverageSaleUpdater', db_handle,
                                          update_every=60).start()

if __name__ == '__main__':
  main()
