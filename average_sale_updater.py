import db_handle
from logging import *

import time

class AverageSaleUpdater(object):
  def __init__(self, db_handle):
    self.db_handle = db_handle

  def Run(self, repeat_every=86400):
    while True:
      for id in self.db_handle.GetAllIds():
        self.db_handle.InsertAverageSale(id)

      time.sleep(repeat_every)
