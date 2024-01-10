from schematics.types import StringType, MD5Type
from uuid import uuid4
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.procedure.models.organization import (
    CommonOrganization,
    Organization as BaseOrganization,
    BusinessOrganization as BaseBusinessOrganization,
)
from openprocurement.tender.core.procedure.models.contact import ContactPoint
from openprocurement.tender.core.procedure.models.address import Address

PROCURING_ENTITY_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")


class Organization(BaseOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class BusinessOrganization(BaseBusinessOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class ContactLessBusinessOrganization(BaseBusinessOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class Buyer(CommonOrganization):
    id = MD5Type(default=lambda: uuid4().hex)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class ProcuringEntity(Organization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))
    kind = StringType(choices=PROCURING_ENTITY_KINDS, required=True)
