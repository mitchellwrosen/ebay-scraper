import config

ERROR = 1
WARNING = 2
INFO = 3

def LOG(type_,  msg):
  if config.kLogging and type_ >= config.kLogging:
    print '%s %s' % ({
      INFO: 'INFO:',
      WARNING: 'WARNING:',
      ERROR: 'ERROR:',
    }[type_], msg)
