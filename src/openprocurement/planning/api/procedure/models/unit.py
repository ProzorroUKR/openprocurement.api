from openprocurement.api.procedure.models.unit import validate_code
from openprocurement.api.procedure.models.unit import (
    Unit as BaseUnit,
)
from openprocurement.planning.api.procedure.context import get_plan


class Unit(BaseUnit):
    def validate_code(self, unit, code):
        validate_code(get_plan(), unit, code)
