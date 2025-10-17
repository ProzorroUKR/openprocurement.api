from schematics.types import BaseType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

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
from openprocurement.api.procedure.utils import to_decimal


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

    def convert_value(self):
        if self.value and isinstance(self.value, float):
            return to_decimal(self.value)
        return self.value

    def convert_values(self):
        if self.values:
            normalized_values = []
            for value in self.values:
                if isinstance(value, float):
                    normalized_values.append(to_decimal(value))
                else:
                    normalized_values.append(value)
            return normalized_values
        return self.values

    @serializable(serialized_name="value", serialize_when_none=False)
    def serialize_value(self):
        return self.convert_value()

    @serializable(serialized_name="values", serialize_when_none=False)
    def serialize_values(self):
        return self.convert_values()


class Item(BaseItem):
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True), default=[])
    unit = ModelType(Unit)
    deliveryAddress = ModelType(Address)
    deliveryDate = ModelType(Period)
    relatedLot = MD5Type()
    relatedBuyer = MD5Type()
    attributes = ListType(ModelType(Attribute, required=True))
