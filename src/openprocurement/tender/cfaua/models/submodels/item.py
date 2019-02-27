# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import Address

from openprocurement.tender.cfaua.models.submodels.periods import PeriodEndRequired
from openprocurement.tender.cfaua.models.submodels.unit import Unit
from openprocurement.tender.core.models import Item as BaseItem


# openprocurement.tender.openua.models.Item
class Item(BaseItem):
    """A good, service, or work to be contracted."""
    class Options:
        roles = RolesFromCsv('Item.csv', relative_to=__file__)
    description_en = StringType(required=True, min_length=1)
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)
    unit = ModelType(Unit)
