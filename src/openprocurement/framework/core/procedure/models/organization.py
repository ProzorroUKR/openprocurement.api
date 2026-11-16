from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.organization import (
    BusinessOrganization,
    ProcuringEntityKind,
)
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.framework.core.procedure.models.address import Address, FullAddress
from openprocurement.framework.core.procedure.models.contact import (
    ContactPoint,
    PatchContactPoint,
)
from openprocurement.framework.core.procedure.models.identifier import (
    Identifier,
    SubmissionIdentifier,
)


class Organization(BaseOrganization):
    contactPoint: BaseContactPoint
    address: Address


class ProcuringEntity(BaseOrganization):
    identifier: Identifier
    additionalIdentifiers: list[Identifier] | None = None
    address: FullAddress
    contactPoint: ContactPoint
    kind: ProcuringEntityKind = ProcuringEntityKind.GENERAL


class PatchProcuringEntity(BaseOrganization):
    name: str | None = None
    identifier: Identifier | None = None
    additionalIdentifiers: list[Identifier] | None = None
    address: FullAddress | None = None
    contactPoint: PatchContactPoint | None = None
    kind: ProcuringEntityKind | None = None


class PatchActiveProcuringEntity(Model):
    contactPoint: PatchContactPoint | None = None


class SubmissionBusinessOrganization(BusinessOrganization):
    identifier: SubmissionIdentifier
    address: FullAddress
    contactPoint: ContactPoint


class ContractBusinessOrganization(BusinessOrganization):
    contactPoint: BaseContactPoint
    address: Address
