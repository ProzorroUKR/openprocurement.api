from enum import StrEnum

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import ContactPoint
from openprocurement.api.procedure.models.identifier import Identifier


class ProcuringEntityKind(StrEnum):
    AUTHORITY = "authority"
    CENTRAL = "central"
    DEFENSE = "defense"
    GENERAL = "general"
    OTHER = "other"
    SOCIAL = "social"
    SPECIAL = "special"


class OrganizationScale(StrEnum):
    MICRO = "micro"
    SME = "sme"
    MID = "mid"
    LARGE = "large"
    NOT_SPECIFIED = "not specified"


class CommonOrganization(Model):
    name: str
    name_en: str | None = None
    name_ru: str | None = None
    identifier: Identifier


class Organization(CommonOrganization):
    additionalIdentifiers: list[Identifier] | None = None
    address: Address
    contactPoint: ContactPoint
    additionalContactPoints: list[ContactPoint] | None = None


class BusinessOrganization(Organization):
    scale: OrganizationScale | None = None
