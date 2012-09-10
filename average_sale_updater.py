import database_handle
import util
from config import logger

class AverageSaleUpdater(object):
  def __init__(self, db_handle):
    self.db_handle = db_handle

  def Run(self, repeat_every=86400):
    while True:
      logger.info('Updating all average sales...')
      for id in self.db_handle.GetAllIds():
        self.db_handle.TrimSales(id)
        self.db_handle.InsertAverageSale(id)

      util.Sleep(repeat_every)
