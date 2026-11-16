from pydantic import Field

from openprocurement.api.procedure.models.item import TechFeatureItemMixin
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.framework.core.procedure.models.framework import Item as BaseItem


class Item(TechFeatureItemMixin, BaseItem):
    description_en: str = Field(min_length=1)
    relatedLot: MD5 | None = None
    relatedBuyer: MD5 | None = None
