from openprocurement.api.models import Model
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import (
    LotValue as BaseLotValue,
    get_tender,
    WeightedValueMixin,
)
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.tender.cfaua.models.submodels.value import Value
from openprocurement.tender.core.validation import validate_lotvalue_value, validate_relatedlot


class LotValue(BaseLotValue, WeightedValueMixin):
    class Options:
        roles = RolesFromCsv("LotValue.csv", relative_to=__file__)

    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    value = ModelType(Value, required=True)

    skip = ("invalid", "deleted", "draft")

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model) and parent.status not in self.skip:
            validate_lotvalue_value(get_tender(parent), data["relatedLot"], value)

    def validate_relatedLot(self, data, relatedLot):
        parent = data["__parent__"]
        if isinstance(parent, Model) and parent.status not in self.skip:
            validate_relatedlot(get_tender(parent), relatedLot)
