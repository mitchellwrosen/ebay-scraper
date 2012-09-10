import config
import ebay_constants
import phone
from config import logger

import inspect
import random
import smtplib
import threading
import time
import urllib
import urllib2
from email.mime.text import MIMEText

def SendEmail_(msg):
  msg['From'] = config.kEmailFrom
  msg['To'] = ', '.join(config.kEmailTo)

  try:
    email_server = smtplib.SMTP(config.kEmailServer)
    email_server.starttls()
    email_server.login(config.kEmailFrom, config.kEmailFromPassword)
    email_server.sendmail(config.kEmailFrom, config.kEmailTo, msg.as_string())
    email_server.quit()
  # SMTPConnectError, SMTPHeloError, SMTPException, SMTPAuthenticationError, ...
  except Exception, e:
    logger.exception(e)

def SendEmail(msg):
  threading.Thread(target=SendEmail_, args=(msg,)).start()

def SendPhoneEmail(phone, link, price, average_price):
  msg = MIMEText('<a href="%(link)s">%(link)s</a>' % link, 'html')
  msg['Subject'] = '%s ($%s, average $%s)' % (phone.ToString(), price,
                                              average_price)
  SendEmail(msg)
  logger.info('Email for %s sent.' % phone.ToString())

'''
Gets the average element in a list.
'''
def Average(list):
  if not list:
    return -1
  return sum(item[0] for item in list) / len(list)

'''
Trims |pct| percent (0-1) from either end of a list, and return the sorted list.
'''
def Trim(list, pct):
  chop_num = int(len(list) * pct)
  if chop_num == 0:
    return sorted(list)
  return sorted(list)[chop_num:-chop_num]

'''
Generates a urllib2.Request object from a url_info dictionary. The search term
(model) is treated separately, because spaces expand to %20 and not %2520.
'''
def GenerateRequest(url_info, search):
  get_params = urllib.urlencode(url_info['get_params'])

  # Replace all + with ' ' and all %xx with %25xx, cause eBay.
  get_params = get_params.replace('+', '%20')
  get_params = get_params.replace('%', '%25')

  # Tack on search string (model).
  get_params += urllib.urlencode({'_nkw': search}).replace('+', '%20')

  return urllib2.Request(url_info['base_url'] + '?' + get_params,
                         '',
                         url_info['headers'])

'''
Converts an "eBay time" (milliseconds since epoch) into a human-readable string.
'''
def EbayTimeToString(ebay_time):
  return time.strftime('%A %b-%d-%Y %H:%M:%S',
                       time.localtime(int(ebay_time) / 1000))

'''
Sleep with a random deviation to un-synchronize threads.
'''
def Sleep(secs):
  time.sleep(random.randrange(secs - 1, secs + 2))

'''
Decorator that surrounds the function in a try/catch block and logs any
thrown exceptions.
'''
def log_exceptions(func):
  def wrapper(self):
    try:
      func(self)
    except Exception, e:
      logger.exception(e)

  return wrapper

