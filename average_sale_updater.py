import db_handle

import logging
import util

class AverageSaleUpdater(object):
  def __init__(self, db_handle):
    self.db_handle = db_handle

  @util.safe
  def Run(self, repeat_every=86400):
    while True:
      logging.info('Updating all average sales...')
      for id in self.db_handle.GetAllIds():
        self.db_handle.TrimSales(id)
        self.db_handle.InsertAverageSale(id)

      util.Sleep(repeat_every)
