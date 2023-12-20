from openprocurement.api.procedure.models.unit import (
    Unit as BaseUnit,
    validate_code,
)
from openprocurement.tender.core.procedure.context import get_tender


class Unit(BaseUnit):

    def validate_code(self, unit, code):
        validate_code(get_tender(), unit, code)


class UnitDeprecated(Unit):

    def validate_code(self, data, value):
        pass
