from pydantic import field_validator

from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.contact import (
    validate_email,
    validate_telephone,
)
from openprocurement.api.procedure.types import (
    Email,
)


class CommonContactPoint(BaseContactPoint):
    @model_field_validator("email")
    def validate_email(self, email):
        validate_email(email, self.telephone)

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, telephone):
        validate_telephone(telephone)
        return telephone


class ContactPoint(CommonContactPoint):
    email: Email


class PatchContactPoint(ContactPoint):
    name: str | None = None
    email: Email | None = None
