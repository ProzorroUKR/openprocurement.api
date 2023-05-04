from openprocurement.api.context import get_now
from openprocurement.api.models import ValidationError, Value, UNIT_CODES, Model
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from schematics.types import StringType
from openprocurement.api.constants import UNIT_CODE_REQUIRED_FROM


class Unit(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    value = ModelType(Value)
    code = StringType(required=True)

    def validate_code(self, data, value):
        validation_date = get_first_revision_date(get_tender(), default=get_now())
        if validation_date >= UNIT_CODE_REQUIRED_FROM:
            if value not in UNIT_CODES:
                raise ValidationError(u"Code should be one of valid unit codes.")


class UnitDeprecated(Unit):

    def validate_code(self, data, value):
        pass
