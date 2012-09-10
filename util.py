import config
import ebay_constants
import phone

import inspect
import logging
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
    logging.error(e)

def SendEmail(msg):
  threading.Thread(target=SendEmail_, args=(msg,)).start()

def SendPhoneEmail(phone, link, price, average_price):
  msg = MIMEText('<a href="%(link)s">%(link)s</a>' % link, 'html')
  msg['Subject'] = '%s ($%s, average $%s)' % (phone.ToString(), price,
                                              average_price)
  SendEmail(msg)
  logging.info('Email for %s sent.' % phone.ToString())

'''
Decorator that surrounds the function in a try/catch block and logs any
thrown exceptions.
'''
def safe(func):
  def wrapper():
    try:
      func()
    except Exception, e:
      # Grab the frame outside wrapper(). Not really the correct frame, since
      # the correct frame would be func()'s frame.
      frame_info = inspect.stack()[1]
      arg_info = inspect.getargvalues(frame_info[0])
      s = '%s:%s %s(' % (frame_info[1], frame_info[2],
                         frame_info[3])
      for arg in arg_info.args:
        s += '%s=%s, ' % (arg, arg_info.locals[arg])
      s += '):'
      logging.error('%s %s' % (s, e))

  return wrapper

'''
Gets the average element in a list.
'''
@safe
def Average(list):
  if not list:
    return -1
  return sum(item[0] for item in list) / len(list)

'''
Trims |pct| percent (0-1) from either end of a list, and return the sorted list.
'''
@safe
def Trim(list, pct):
  chop_num = int(len(list) * pct)
  if chop_num == 0:
    return sorted(list)
  return sorted(list)[chop_num:-chop_num]

'''
Generates a urllib2.Request object from a url_info dictionary. The search term
(model) is treated separately, because spaces expand to %20 and not %2520.
'''
@safe
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
@safe
def EbayTimeToString(ebay_time):
  return time.strftime('%A %b-%d-%Y %H:%M:%S',
                       time.localtime(int(ebay_time) / 1000))

'''
Sleep with a random deviation to un-synchronize threads.
'''
@safe
def Sleep(secs):
  time.sleep(random.randrange(secs - 1, secs + 2))
