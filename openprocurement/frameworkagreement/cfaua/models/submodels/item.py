from openprocurement.tender.openua.models import Item as BaseItem
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import Address

from openprocurement.frameworkagreement.cfaua.models.submodels.periods import PeriodEndRequired

class Item(BaseItem):
    """A good, service, or work to be contracted."""

    description_en = StringType(required=True, min_length=1)
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)