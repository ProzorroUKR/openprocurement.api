from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.organization import (
    PROCURING_ENTITY_KIND_CHOICES,
    BusinessOrganization,
)
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.procedure.types import ListType, ModelType
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
    contactPoint = ModelType(BaseContactPoint, required=True)
    address = ModelType(Address, required=True)


class ProcuringEntity(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(FullAddress, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES, default=ProcuringEntityKind.GENERAL, required=True)

    def validate_identifier(self, data, identifier):
        pass


class PatchProcuringEntity(BaseOrganization):
    name = StringType()
    identifier = ModelType(Identifier)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(FullAddress)
    contactPoint = ModelType(PatchContactPoint)
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES)

    def validate_identifier(self, data, identifier):
        pass


class PatchActiveProcuringEntity(Model):
    contactPoint = ModelType(PatchContactPoint)


class SubmissionBusinessOrganization(BusinessOrganization):
    identifier = ModelType(SubmissionIdentifier, required=True)
    address = ModelType(FullAddress, required=True)
    contactPoint = ModelType(ContactPoint, required=True)


class ContractBusinessOrganization(BusinessOrganization):
    contactPoint = ModelType(BaseContactPoint, required=True)
    address = ModelType(Address, required=True)
