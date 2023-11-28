from openprocurement.api.models import Unit as BaseUnit, validate_unit_code


class Unit(BaseUnit):
    def validate_code(self, data, value):
        validate_unit_code(value)
