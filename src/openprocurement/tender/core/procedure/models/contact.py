from typing import Literal

from pydantic import field_validator

from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.contact import (
    validate_email,
    validate_telephone,
)


class ContactPoint(BaseContactPoint):
    @model_field_validator("email")
    def validate_email(self, email):
        validate_email(email, self.telephone)

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, telephone):
        validate_telephone(telephone)
        return telephone


class ProcuringEntityContactPoint(ContactPoint):
    availableLanguage: Literal["uk", "en", "ru"] | None = None
