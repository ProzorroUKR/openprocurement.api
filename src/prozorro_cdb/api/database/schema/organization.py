from typing import Any

from pydantic import EmailStr, HttpUrl

from openprocurement.api.procedure.models.organization import (
    OrganizationScale,
    ProcuringEntityKind,
)
from prozorro_cdb.api.database.schema.common import BaseModel


class Identifier(BaseModel):
    id: Any
    scheme: str
    legalName: str | None = None
    legalName_en: str | None = None
    legalName_ru: str | None = None
    uri: HttpUrl | None = None


class ContactPoint(BaseModel):
    name: str
    name_en: str | None = None
    name_ru: str | None = None
    email: EmailStr | None = None
    telephone: str | None = None
    faxNumber: str | None = None
    url: HttpUrl | None = None


class Classification(BaseModel):
    id: str
    scheme: str
    description: str
    description_en: str | None = None
    description_ru: str | None = None
    uri: HttpUrl | None = None


class AddressClassification(Classification):
    pass


class Address(BaseModel):
    streetAddress: str | None = None
    locality: str | None = None
    region: str | None = None
    postalCode: str | None = None
    countryName: str
    countryName_en: str | None = None
    countryName_ru: str | None = None
    addressDetails: list[AddressClassification] | None = None


class Organization(BaseModel):
    """An organization"""

    name: str
    name_en: str | None = None
    identifier: Identifier
    additionalIdentifiers: list[Identifier] | None = None
    additionalContactPoints: list[ContactPoint] | None = None
    address: Address | None = None
    contactPoint: ContactPoint | None = None
    contract_owner: str | None = None


class SignerInfo(BaseModel):
    name: str
    email: EmailStr
    telephone: str
    iban: str
    position: str
    authorizedBy: str


class Supplier(Organization):
    """Supplier organization"""

    scale: OrganizationScale | None = None
    signerInfo: SignerInfo | None = None


class Buyer(Organization):
    """Buyer (procuring entity) organization"""

    kind: ProcuringEntityKind | None = None
    signerInfo: SignerInfo | None = None


class ProcuringEntity(Organization):
    kind: ProcuringEntityKind = ProcuringEntityKind.GENERAL
