import ebay_constants

import logging
import random
import time
import urllib
import urllib2

def SendEmail_(msg):
  msg['From'] = 'ebayscraper@gmail.com'
  msg['To'] = 'mitchellwrosen@gmail.com'

  email_server = smtplib.SMTP(smtp.gmail.com:587)
  email_server.starttls()
  email_server.login('ebayscraper@gmail.com', 'ebayscraper')
  email_server.sendmail('ebayscraper@gmail.com', 'mitchellwrosen@gmail.com',
                        text)
  email_server.quit()
  logging.info('Email for %s sent.' % phone.ToString())

def SendEmail(msg):
  threading.Thread(target=SendEmail_, args=(msg,))

def SendPhoneEmail(phone, link, price, average_price):
  msg = email.MIMEText('<a href="%s">%s</a>' % (link, link), 'html')
  msg['Subject'] = '%s ($%s, average $%s)' % (phone.ToString(), price,
                                              average_price)
  SendEmail(msg)

'''
Decorator that surrounds the function in a try/catch block and sends an email
containing any exceptions. Note that the email function itself needs to be
void of any possible exceptions =(.
'''
def safe(func):
  def wrapper():
    try:
      func()
    except Exception, e:
      msg = email.MIMEText(e, 'plain')
      msg['Subject'] = '%s exception' % func.__name__
      SendEmail(msg)

  return wrapper

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


