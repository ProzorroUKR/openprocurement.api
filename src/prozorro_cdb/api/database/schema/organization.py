from typing import Any, Literal, Optional

from pydantic import EmailStr, HttpUrl

from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from prozorro_cdb.api.database.schema.common import BaseModel


class Identifier(BaseModel):
    id: Any
    scheme: str
    legalName: Optional[str] = None
    legalName_en: Optional[str] = None
    legalName_ru: Optional[str] = None
    uri: Optional[HttpUrl] = None


class ContactPoint(BaseModel):
    name: str
    name_en: Optional[str] = None
    name_ru: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    faxNumber: Optional[str] = None
    url: Optional[HttpUrl] = None


class Classification(BaseModel):
    id: str
    scheme: str
    description: str
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    uri: Optional[HttpUrl] = None


class AddressClassification(Classification):
    pass


class Address(BaseModel):
    streetAddress: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postalCode: Optional[str] = None
    countryName: str
    countryName_en: Optional[str] = None
    countryName_ru: Optional[str] = None
    addressDetails: Optional[list[AddressClassification]] = None


class Organization(BaseModel):
    """An organization"""

    name: str
    name_en: Optional[str] = None
    identifier: Identifier
    additionalIdentifiers: Optional[list[Identifier]] = None
    additionalContactPoints: Optional[list[ContactPoint]] = None
    address: Optional[Address] = None
    contactPoint: Optional[ContactPoint] = None
    contract_owner: Optional[str] = None


class SignerInfo(BaseModel):
    name: str
    email: EmailStr
    telephone: str
    iban: str
    position: str
    authorizedBy: str


class Supplier(Organization):
    """Supplier organization"""

    scale: Optional[Literal["micro", "sme", "large"]] = None
    signerInfo: Optional[SignerInfo] = None


class Buyer(Organization):
    """Buyer (procuring entity) organization"""

    kind: Optional[ProcuringEntityKind] = None
    signerInfo: Optional[SignerInfo] = None


class ProcuringEntity(Organization):
    kind: ProcuringEntityKind = ProcuringEntityKind.GENERAL
