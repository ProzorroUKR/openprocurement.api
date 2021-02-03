# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.types import StringType
from openprocurement.api.models import Model, DecimalType
from openprocurement.api.roles import RolesFromCsv


class ParameterContract(Model):
    class Options:
        serialize_when_none = False
        roles = RolesFromCsv("Parameter.csv", relative_to=__file__)

    code = StringType(required=True)
    value = DecimalType(required=True)

    def validate_code(self, data, code):
        agreement = data["__parent__"]["__parent__"]
        if isinstance(agreement, Model) and code not in [i.code for i in (agreement.features or [])]:
            raise ValidationError("code should be one of feature code.")

    def validate_value(self, data, value):
        agreement = data["__parent__"]["__parent__"]
        if isinstance(agreement, Model):
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (agreement.features or [])])
            if data["code"] in codes and value not in codes[data["code"]]:
                raise ValidationError("value should be one of feature value.")
