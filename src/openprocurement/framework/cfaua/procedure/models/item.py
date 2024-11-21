from schematics.types import MD5Type

from openprocurement.framework.core.procedure.models.framework import Item as BaseItem
from openprocurement.api.procedure.models.item import TechFeatureItemMixin


class Item(TechFeatureItemMixin, BaseItem):
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()
