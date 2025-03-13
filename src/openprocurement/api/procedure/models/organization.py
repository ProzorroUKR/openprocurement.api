from enum import StrEnum

from schematics.types import StringType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import ContactPoint
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import ListType, ModelType


class ProcuringEntityKind(StrEnum):
    AUTHORITY = "authority"
    CENTRAL = "central"
    DEFENSE = "defense"
    GENERAL = "general"
    OTHER = "other"
    SOCIAL = "social"
    SPECIAL = "special"


PROCURING_ENTITY_KIND_CHOICES = (
    ProcuringEntityKind.AUTHORITY.value,
    ProcuringEntityKind.CENTRAL.value,
    ProcuringEntityKind.DEFENSE.value,
    ProcuringEntityKind.GENERAL.value,
    ProcuringEntityKind.OTHER.value,
    ProcuringEntityKind.SOCIAL.value,
    ProcuringEntityKind.SPECIAL.value,
)


class OrganizationScale(StrEnum):
    MICRO = "micro"
    SME = "sme"
    MID = "mid"
    LARGE = "large"
    NOT_SPECIFIED = "not specified"


ORGANIZATION_SCALE_CHOICES = [
    OrganizationScale.MICRO.value,
    OrganizationScale.SME.value,
    OrganizationScale.MID.value,
    OrganizationScale.LARGE.value,
    OrganizationScale.NOT_SPECIFIED.value,
]


class CommonOrganization(Model):
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)


class Organization(CommonOrganization):
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier, required=True))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class BusinessOrganization(Organization):
    scale = StringType(choices=ORGANIZATION_SCALE_CHOICES)
