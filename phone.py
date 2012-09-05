import ebay_constants

class Phone(object):
  def __init__(self, model, brand, storage_capacity, carrier, cond):
    self.model = model
    self.brand = brand
    self.storage_capacity = storage_capacity
    self.carrier = carrier
    self.cond = cond
    self.ebay_cond = {
      'Used': ebay_constants.kConditionUsed,
      'New': ebay_constants.kConditionNew,
    }[self.cond]

