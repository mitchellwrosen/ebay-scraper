import config
import db_handle
import scraper

import MySQLdb
import threading

if __name__ == '__main__':
  url_info = {
    'base_url' : config.kBaseUrl,
    'get_params' : {},
    'headers' : config.kHeaders,
  }


  db_handle = db_handle.PhoneDatabaseHandle(config.kDatabaseInfo)
  with db_handle:
    for phone in config.kPhones:
      #ended_scraper = scraper.PhoneEndedScraper(db_handle, url_info, phone,
      #                                          repeat_every=10)
      #threading.Thread(target=ended_scraper.Run).start()

      bin_scraper = scraper.PhoneBINScraper(db_handle, url_info, phone,
                                            repeat_every=5)
      threading.Thread(target=bin_scraper.Run).start()
