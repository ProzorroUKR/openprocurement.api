from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.base import DecimalType
from openprocurement.tender.cfaselectionua.procedure.utils import equals_decimal_and_corrupted
from openprocurement.tender.core.procedure.models.parameter import (
    PatchParameter as BasePatchParameter,
    Parameter as BaseParameter,
)
from schematics.exceptions import ValidationError


def validate_value(data, value):
    tender = get_tender()
    for feature in tender.get("features", ""):
        if data["code"] == feature["code"]:
            if not any(equals_decimal_and_corrupted(value, e["value"])
                       for e in feature["enum"]):
                raise ValidationError("value should be one of feature value.")


class Parameter(BaseParameter):
    value = DecimalType(required=True)

    def validate_value(self, data, value):
        validate_value(data, value)


class PatchParameter(BasePatchParameter):
    value = DecimalType()

    def validate_value(self, data, value):
        return value

