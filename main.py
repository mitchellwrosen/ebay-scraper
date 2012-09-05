import average_sale_updater
import config
import db_handle
import scraper

import threading

if __name__ == '__main__':
  db_handle = db_handle.PhoneDatabaseHandle(config.kDatabaseInfo)
  for phone in config.kPhones:
    ended_scraper = scraper.PhoneEndedScraper(db_handle, config.kUrlInfo, phone,
                                              repeat_every=10)
    threading.Thread(target=ended_scraper.Run).start()

    bin_scraper = scraper.PhoneBINScraper(db_handle, config.kUrlInfo, phone,
                                          repeat_every=5)
    threading.Thread(target=bin_scraper.Run).start()

  # Spawn a thread to update averagesale periodically.
  average_sale_updater = average_sale_updater.AverageSaleUpdater(db_handle)
  threading.Thread(target=average_sale_updater.Run,
                   kwargs={'repeat_every': 60}).start()
