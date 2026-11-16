from typing import Literal

from pydantic import field_validator

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import (
    Organization,
    ProcuringEntityKind,
)
from openprocurement.framework.core.procedure.models.contact import (
    CommonContactPoint as BaseContactPoint,
)


class ContactPoint(BaseContactPoint):
    availableLanguage: Literal["uk", "en", "ru"] = "uk"

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, value):
        return value


class ProcuringEntity(Organization):
    """An organization."""

    kind: ProcuringEntityKind | None = None
    contactPoint: ContactPoint
    additionalContactPoints: list[ContactPoint] | None = None
    address: Address
