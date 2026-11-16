from pydantic import field_validator

from openprocurement.api.constants_env import VALIDATE_ADDRESS_FROM
from openprocurement.api.procedure.models.address import Address as BaseAddress
from openprocurement.api.procedure.models.address import validate_country_name, validate_region
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import (
    OrganizationScale,
    ProcuringEntityKind,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.contracting.core.procedure.models.contact import ContactPoint
from openprocurement.tender.core.procedure.utils import tender_created_after


class Address(BaseAddress):
    @field_validator("countryName")
    @classmethod
    def validate_country_name(cls, country_name: str) -> str:
        if tender_created_after(VALIDATE_ADDRESS_FROM):
            validate_country_name(country_name)
        return country_name

    @model_field_validator("region")
    def validate_region(self, value):
        if tender_created_after(VALIDATE_ADDRESS_FROM):
            validate_region(self.countryName, value)


class Organization(Model):
    """An organization."""

    name: str
    name_en: str | None = None
    name_ru: str | None = None
    identifier: Identifier
    additionalIdentifiers: list[Identifier] | None = None
    additionalContactPoints: list[ContactPoint] | None = None
    address: Address | None = None
    contactPoint: ContactPoint | None = None
    contract_owner: str | None = None


class Supplier(Organization):
    scale: OrganizationScale | None = None
    signerInfo: SignerInfo | None = None


class Buyer(Organization):
    kind: ProcuringEntityKind | None = None
    signerInfo: SignerInfo | None = None
