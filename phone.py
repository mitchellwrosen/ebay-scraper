import ebay_constants
import util

class Phone(object):
  def __init__(self, model, brand, cond, carrier, storage_capacity=None,
               color=None):
    self.model = model
    self.brand = brand
    self.cond = cond
    self.carrier = carrier
    self.storage_capacity = storage_capacity
    self.color = color

    self.ebay_cond = {
      ebay_constants.kConditionKeyNew: ebay_constants.kConditionValueNew,
      ebay_constants.kConditionKeyNewOther: ebay_constants.kConditionValueNewOther,
      ebay_constants.kConditionKeyManufacturerRefurbished: ebay_constants.kConditionValueManufacturerRefurbished,
      ebay_constants.kConditionKeySellerRefurbished: ebay_constants.kConditionValueSellerRefurbished,
      ebay_constants.kConditionKeyUsed: ebay_constants.kConditionValueUsed,
      ebay_constants.kConditionKeyForParts: ebay_constants.kConditionValueForParts,
    }[self.cond]

  @util.safe
  def ToString(self):
    attrs = [self.model, self.brand, self.cond, self.carrier,
             self.storage_capacity, self.color]
    return ' '.join([attr for attr in attrs if attr])
