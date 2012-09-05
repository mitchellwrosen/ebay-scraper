import ebay_constants

class Phone(object):
  def __init__(self, model, brand, cond, storage_capacity=None, carrier=None,
               color=None):
    self.model = model
    self.brand = brand
    self.cond = cond
    self.storage_capacity = storage_capacity
    self.carrier = carrier
    self.color = color

    self.ebay_cond = {
      ebay_constants.kConditionKeyNew: ebay_constants.kConditionValueNew,
      ebay_constants.kConditionKeyNewOther: ebay_constants.kConditionValueNewOther,
      ebay_constants.kConditionKeyManufacturerRefurbished: ebay_constants.kConditionValueManufacturerRefurbished,
      ebay_constants.kConditionKeySellerRefurbished: ebay_constants.kConditionValueSellerRefurbished,
      ebay_constants.kConditionKeyUsed: ebay_constants.kConditionValueUsed,
      ebay_constants.kConditionKeyForParts: ebay_constants.kConditionValueForParts,
    }[self.cond]
