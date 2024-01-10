from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.framework.cfaua.procedure.models.value import Value


class UnitPrice(Model):
    relatedItem = StringType()
    value = ModelType(Value)
