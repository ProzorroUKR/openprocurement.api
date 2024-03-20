from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.organization import BusinessOrganization
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.core.procedure.models.address import Address, FullAddress
from openprocurement.framework.core.procedure.models.contact import (
    SubmissionContactPoint,
)
from openprocurement.framework.core.procedure.models.identifier import (
    SubmissionIdentifier,
)


class Organization(BaseOrganization):
    contactPoint = ModelType(BaseContactPoint, required=True)
    address = ModelType(Address, required=True)


class SubmissionBusinessOrganization(BusinessOrganization):
    identifier = ModelType(SubmissionIdentifier, required=True)
    address = ModelType(FullAddress, required=True)
    contactPoint = ModelType(SubmissionContactPoint, required=True)


class ContractBusinessOrganization(BusinessOrganization):
    contactPoint = ModelType(BaseContactPoint, required=True)
    address = ModelType(Address, required=True)
