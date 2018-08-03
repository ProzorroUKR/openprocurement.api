from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import (
    Value,
    Model
    )


class UnitPrice(Model):
    # TODO: validate relatedItem?
    relatedItem = StringType()
    value = ModelType(Value)