from openprocurement.api.procedure.models.unit import Unit as BaseUnit, validate_code


class Unit(BaseUnit):
    def validate_code(self, unit, code):
        validate_code(unit, code)
