from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.contact import validate_email


class ContactPoint(BaseContactPoint):
    availableLanguage: str | None = None

    @model_field_validator("email")
    def validate_email(self, email):
        validate_email(email, self.telephone)
