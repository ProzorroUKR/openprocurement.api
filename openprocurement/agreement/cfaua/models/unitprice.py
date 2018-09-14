from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import (
    Model
)
from openprocurement.agreement.core.models.value import Value


class UnitPrice(Model):
    class Options:
        roles = RolesFromCsv('UnitPrice.csv', relative_to=__file__)

    # TODO: validate relatedItem?
    relatedItem = StringType()
    value = ModelType(Value)
