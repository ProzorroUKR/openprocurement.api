from uuid import uuid4

from schematics.types import MD5Type, StringType

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.procedure.models.organization import (
    BusinessOrganization as BaseBusinessOrganization,
)
from openprocurement.api.procedure.models.organization import CommonOrganization
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.contact import ContactPoint

PROCURING_ENTITY_KINDS = (
    "authority",
    "central",
    "defense",
    "general",
    "other",
    "social",
    "special",
)


class Organization(BaseOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class BusinessOrganization(BaseBusinessOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))
    scale = StringType(choices=SCALE_CODES, required=True)


class ContactLessBusinessOrganization(BusinessOrganization):
    contactPoint = ModelType(ContactPoint)


class Buyer(CommonOrganization):
    id = MD5Type(default=lambda: uuid4().hex)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class ProcuringEntity(Organization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))
    kind = StringType(choices=PROCURING_ENTITY_KINDS, required=True)
