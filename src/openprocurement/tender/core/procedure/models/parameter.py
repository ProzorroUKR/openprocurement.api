from schematics.exceptions import ValidationError
from schematics.types import FloatType, StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model


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
