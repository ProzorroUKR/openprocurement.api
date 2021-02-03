# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.types import StringType
from openprocurement.api.models import Model, DecimalType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.agreement.core.utils import get_agreement


class Parameter(Model):
    class Options:
        serialize_when_none = False
        roles = RolesFromCsv("Parameter.csv", relative_to=__file__)

    code = StringType(required=True)
    value = DecimalType(required=True)

    def validate_code(self, data, code):
        if isinstance(data["__parent__"], Model) and code not in [
            i.code for i in (get_agreement(data["__parent__"]).features or [])
        ]:
            raise ValidationError("code should be one of feature code.")

    def validate_value(self, data, value):
        if isinstance(data["__parent__"], Model):
            agreement = get_agreement(data["__parent__"])
            codes = dict([(i.code, [x.value for x in i.enum]) for i in (agreement.features or [])])
            if data["code"] in codes and value not in codes[data["code"]]:
                raise ValidationError("value should be one of feature value.")
