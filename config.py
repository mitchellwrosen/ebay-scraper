import ebay_constants
import phone

# 0=None; 1=Errors; 2=Errors,Warnings; 3=Errors,Warnings,Info
kLogging = 3

kPhones = [
  phone.Phone('Galaxy Nexus SCH-I515', 'Samsung',
              ebay_constants.kConditionKeyNew, storage_capacity='32 GB',
              carrier='Verizon'),
  phone.Phone('Galaxy Nexus SCH-I515', 'Samsung',
              ebay_constants.kConditionKeyNewOther, storage_capacity='32 GB',
              carrier='Verizon'),
  phone.Phone('Galaxy Nexus SCH-I515', 'Samsung',
              ebay_constants.kConditionKeyManufacturerRefurbished,
              storage_capacity='32 GB', carrier='Verizon'),
  phone.Phone('Galaxy Nexus SCH-I515', 'Samsung',
              ebay_constants.kConditionKeySellerRefurbished,
              storage_capacity='32 GB', carrier='Verizon'),
  phone.Phone('Galaxy Nexus SCH-I515', 'Samsung',
              ebay_constants.kConditionKeyUsed, storage_capacity='32 GB',
              carrier='Verizon'),
  phone.Phone('Galaxy Nexus SCH-I515', 'Samsung',
              ebay_constants.kConditionKeyForParts, storage_capacity='32 GB',
              carrier='Verizon'),
  phone.Phone('iPhone 4', 'Apple', '16 GB', 'AT&T', 'New'),
]

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
