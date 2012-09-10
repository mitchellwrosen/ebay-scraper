import database_handle
import threading
import util
from config import logger

class AverageSaleUpdater(threading.Thread):
  def __init__(self, name, db_handle, update_every=86400):
    threading.Thread.__init__(self, name=name)

    self.db_handle = db_handle
    self.update_every = update_every

  @util.log_exceptions
  def run(self):
    logger.info('Running.')
    while True:
      self.Update()
      util.Sleep(self.update_every)

  def Update(self):
      logger.info('Updating all average sales.')
      for id in self.db_handle.GetAllIds():
        self.db_handle.TrimSales(id)
        self.db_handle.InsertAverageSale(id)
