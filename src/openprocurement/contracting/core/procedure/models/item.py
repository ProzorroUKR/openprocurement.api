from schematics.types import BaseType, MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import (
    AdditionalClassification as BaseAdditionalClassification,
)
from openprocurement.api.procedure.models.item import (
    CPVClassification as BaseCPVClassification,
)
from openprocurement.api.procedure.models.item import Item as BaseItem
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import ListType


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class AdditionalClassification(BaseAdditionalClassification):
    def validate_id(self, data, code):
        pass


class Attribute(Model):
    name = StringType(required=True)
    unit = ModelType(Unit)
    values = ListType(BaseType(required=True))
    value = BaseType()


class Item(BaseItem):
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True), default=[])
    unit = ModelType(Unit)
    deliveryAddress = ModelType(Address)
    deliveryDate = ModelType(Period)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()
    attributes = ListType(ModelType(Attribute, required=True))
