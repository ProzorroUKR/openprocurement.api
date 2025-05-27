from uuid import uuid4

from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import (
    ORGANIZATION_SCALE_CHOICES,
    PROCURING_ENTITY_KIND_CHOICES,
)
from openprocurement.api.procedure.models.organization import (
    BusinessOrganization as BaseBusinessOrganization,
)
from openprocurement.api.procedure.models.organization import CommonOrganization
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.contact import ContactPoint


class Organization(BaseOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class BusinessOrganization(BaseBusinessOrganization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))
    scale = StringType(choices=ORGANIZATION_SCALE_CHOICES, required=True)


class Buyer(CommonOrganization):
    id = MD5Type(default=lambda: uuid4().hex)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES)
    signerInfo = ModelType(SignerInfo)


class Supplier(BusinessOrganization):
    signerInfo = ModelType(SignerInfo)


class ContactLessSupplier(Supplier):
    contactPoint = ModelType(ContactPoint)


class ProcuringEntity(Organization):
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES, required=True)
    signerInfo = ModelType(SignerInfo)
