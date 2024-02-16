import standards
from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ModelType

unit_codes = standards.load("unit_codes/recommended.json")
UNIT_CODES = unit_codes.keys()


class Unit(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    value = ModelType(Value)
    code = StringType(required=True)


def validate_code(unit, code):
    if code not in UNIT_CODES:
        raise ValidationError("Code should be one of valid unit codes.")
