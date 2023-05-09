from openprocurement.api.models import ValidationError, Value, UNIT_CODES, Model
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.utils import tender_created_after
from schematics.types import StringType
from openprocurement.api.constants import UNIT_CODE_REQUIRED_FROM


class Unit(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    value = ModelType(Value)
    code = StringType(required=True)

    def validate_code(self, data, value):
        if tender_created_after(UNIT_CODE_REQUIRED_FROM):
            if value not in UNIT_CODES:
                raise ValidationError(u"Code should be one of valid unit codes.")


class UnitDeprecated(Unit):

    def validate_code(self, data, value):
        pass
