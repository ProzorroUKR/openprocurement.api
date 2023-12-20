from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.constants import UNIT_CODE_REQUIRED_FROM
from openprocurement.api.models import Value, Model, UNIT_CODES
from openprocurement.api.procedure.models.base import ModelType
from openprocurement.api.procedure.utils import is_obj_const_active


class Unit(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    value = ModelType(Value)
    code = StringType(required=True)


def validate_code(obj, unit, code):
    if is_obj_const_active(obj, UNIT_CODE_REQUIRED_FROM):
        if code not in UNIT_CODES:
            raise ValidationError(u"Code should be one of valid unit codes.")
