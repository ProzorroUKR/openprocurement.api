from schematics.types import BaseType, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.item import Item as BaseItem
from openprocurement.tender.core.procedure.models.unit import Unit


class Attribute(Model):
    name = StringType(required=True)
    unit = ModelType(Unit)
    values = ListType(BaseType(required=True))


class Item(BaseItem):
    attributes = ListType(ModelType(Attribute, required=True))
    unit = ModelType(Unit)
