# Set to True to output some information to the console.
kLogging = True

kPhones = [
   ('Galaxy Nexus', 'Samsung', '32 GB', 'Verizon', 'Used'),
   #('iPhone 4', 'Apple', '16 GB', 'AT&T', 'New'),
]

# Indexes into phone tuples.
kPhoneIndexModel = 0
kPhoneIndexBrand = 1
kPhoneIndexSize = 2
kPhoneIndexCarrier = 3
kPhoneIndexCondition = 4

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
  'base_url': 'http://www.ebay.com/sch/rss/?',
  'get_params': {},
  'headers': {
    # Chrome 22 user agent string, cause I'm hella cool like that.
    'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 '
                   '(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'),
  },
}
