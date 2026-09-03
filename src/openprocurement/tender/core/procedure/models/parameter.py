from schematics.exceptions import ValidationError
from schematics.types import FloatType, StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import DecimalType, StringDecimalType
from openprocurement.tender.core.procedure.utils import equals_decimal_and_corrupted


class Parameter(Model):
    code = StringType(required=True)
    value = FloatType(required=True)

    def validate_code(self, data, code):
        if code is not None:  # can be true for patch model
            tender = get_tender()
            if not any(i["code"] == code for i in tender.get("features", "")):
                raise ValidationError("code should be one of feature code.")

    def validate_value(self, data, value):
        if value is not None:  # can be true for patch model
            tender = get_tender()
            for feature in tender.get("features", ""):
                if data["code"] == feature["code"]:
                    if not any(float(e["value"]) == value for e in feature["enum"]):
                        raise ValidationError("value should be one of feature value.")


class PatchParameter(Parameter):
    code = StringType()
    value = FloatType()


# --- CFA selection: decimal parameters ---


def validate_cfa_selection_parameter_value(data, value):
    tender = get_tender()
    for feature in tender.get("features", ""):
        if data["code"] == feature["code"]:
            if not any(equals_decimal_and_corrupted(value, e["value"]) for e in feature["enum"]):
                raise ValidationError("value should be one of feature value.")


class CFASelectionParameter(Parameter):
    value = StringDecimalType(required=True)

    def validate_value(self, data, value):
        validate_cfa_selection_parameter_value(data, value)


class CFASelectionPatchParameter(PatchParameter):
    value = StringDecimalType()

    def validate_value(self, data, value):
        return value


def validate_cfa_selection_parameter_contracts(features, contracts):
    options = {f.code: {e.value for e in f.enum} for f in features or []}
    for contract in contracts or []:
        for param in contract.parameters or []:
            if param.code not in options:
                raise ValidationError("code should be one of feature code.")

            if param.value not in options[param.code]:
                raise ValidationError("value should be one of feature value.")


class CFASelectionParameterContract(Model):
    code = StringType(required=True)
    value = DecimalType(required=True)
