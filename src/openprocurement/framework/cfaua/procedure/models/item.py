from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.models.item import TechFeatureItemMixin
from openprocurement.framework.core.procedure.models.framework import Item as BaseItem


class Item(TechFeatureItemMixin, BaseItem):
    description_en = StringType(required=True, min_length=1)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()
