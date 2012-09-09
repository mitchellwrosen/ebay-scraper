import ebay_constants
import phone

import logging

kLogLevel = logging.INFO

# In main.py, populate kPhones with a call to PopulatePhones() for each phone in
# kPhoneTemplates.
kPhones = []
kPhoneTemplates = [
  {
    'model': 'Galaxy Nexus',
    'brand': 'Samsung',
    'conditions': ebay_constants.kAllConditions,
    'carriers': ['Sprint', 'Unlocked', 'Verizon'],
    'storage_capacities': ['16GB', '32 GB'],
    'colors': [None],
  },
  {
    'model': 'iPhone 4S',
    'brand': 'Apple',
    'conditions': ebay_constants.kAllConditions,
    'carriers': ['AT&T', 'Sprint', 'Unlocked', 'Verizon'],
    'storage_capacities': ['16 GB', '32 GB', '64 GB'],
    'colors': ['White', 'Black'],
  }
]
def PopulatePhones(model, brand, conditions, carriers, storage_capacities,
                   colors):
  for color in colors:
    for storage_capacity in storage_capacities:
      for carrier in carriers:
        for cond in conditions:
          kPhones.append(phone.Phone(model, brand, cond, carrier,
                                     storage_capacity=storage_capacity,
                                     color=color))

# The percentage of sales to trim from either end, before calculating average
# sale.
kTrimPercentage = .25

kDatabaseInfo = {
  'host': 'localhost',
  'user': 'mitchell',
  'passwd': 'password',
  'db': 'ebay_scraper_data',
}

kUrlInfo = {
  'base_url': 'http://www.ebay.com/sch/rss/',
  'get_params': {},
  'headers': {
    # Chrome 22 user agent string, cause I'm hella cool like that.
    'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 '
                   '(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'),
  },
}
