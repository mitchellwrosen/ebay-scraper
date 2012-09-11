import database_handle
import util
from config import logger

import threading
import time

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
      for id in self.db_handle.GetAllIds():
        logger.info('Updating average sale for phone with id %d.' % id)
        self.db_handle.TrimSales(id)
        self.db_handle.InsertAverageSale(id)
        time.sleep(1)
