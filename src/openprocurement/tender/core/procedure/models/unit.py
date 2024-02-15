from openprocurement.api.constants import UNIT_CODE_REQUIRED_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.unit import Unit as BaseUnit
from openprocurement.api.procedure.models.unit import validate_code
from openprocurement.api.procedure.utils import is_obj_const_active


class Unit(BaseUnit):
    def validate_code(self, unit, code):
        if is_obj_const_active(get_tender(), UNIT_CODE_REQUIRED_FROM):
            validate_code(unit, code)
