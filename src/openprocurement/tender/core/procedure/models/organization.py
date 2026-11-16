from uuid import uuid4

from pydantic import Field

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import (
    BusinessOrganization as BaseBusinessOrganization,
)
from openprocurement.api.procedure.models.organization import (
    CommonOrganization,
    OrganizationScale,
    ProcuringEntityKind,
)
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.tender.core.procedure.models.contact import (
    ContactPoint,
    ProcuringEntityContactPoint,
)


class Organization(BaseOrganization):
    address: Address
    contactPoint: ContactPoint
    additionalContactPoints: list[ContactPoint] | None = None


class BusinessOrganization(BaseBusinessOrganization):
    address: Address
    contactPoint: ContactPoint
    additionalContactPoints: list[ContactPoint] | None = None
    scale: OrganizationScale


class Buyer(CommonOrganization):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    address: Address | None = None
    kind: ProcuringEntityKind | None = None
    signerInfo: SignerInfo | None = None
    contract_owner: str | None = None


class Supplier(BusinessOrganization):
    signerInfo: SignerInfo | None = None
    contract_owner: str | None = None


class ContactLessSupplier(Supplier):
    contactPoint: ContactPoint | None = None


class ProcuringEntity(Organization):
    address: Address
    contactPoint: ProcuringEntityContactPoint | None = None
    additionalContactPoints: list[ProcuringEntityContactPoint] | None = None
    kind: ProcuringEntityKind
    signerInfo: SignerInfo | None = None
    contract_owner: str | None = None
