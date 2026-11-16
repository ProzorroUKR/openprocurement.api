from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import validate_telephone
from openprocurement.api.procedure.types import Email


class SignerInfo(Model):
    name: str = Field(min_length=1)
    email: Email = Field(min_length=1)
    telephone: str = Field(min_length=1)
    iban: str = Field(min_length=15, max_length=33)
    position: str = Field(min_length=1)
    authorizedBy: str = Field(min_length=1)

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, value: str) -> str:
        validate_telephone(value)
        return value
