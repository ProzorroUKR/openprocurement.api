import standards
from pydantic import field_validator

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value

unit_codes = standards.load("unit_codes/recommended.json")
UNIT_CODES = unit_codes.keys()


class Unit(Model):
    name: str | None = None
    name_en: str | None = None
    name_ru: str | None = None
    value: Value | None = None
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, code: str) -> str:
        if code not in UNIT_CODES:
            raise ValueError("Code should be one of valid unit codes.")
        return code
