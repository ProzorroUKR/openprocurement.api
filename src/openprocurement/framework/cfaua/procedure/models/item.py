from schematics.types import MD5Type

from openprocurement.api.procedure.models.item import TechFeatureItemMixin
from openprocurement.framework.core.procedure.models.framework import Item as BaseItem


class Item(TechFeatureItemMixin, BaseItem):
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()
