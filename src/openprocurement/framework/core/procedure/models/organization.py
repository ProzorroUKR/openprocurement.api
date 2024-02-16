from schematics.types import StringType

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.organization import (
    BusinessOrganization as BaseBusinessOrganization,
)
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


class SubmissionBusinessOrganization(BaseBusinessOrganization):
    identifier = ModelType(SubmissionIdentifier, required=True)
    address = ModelType(FullAddress, required=True)
    contactPoint = ModelType(SubmissionContactPoint, required=True)
    scale = StringType(choices=SCALE_CODES)


class ContractBusinessOrganization(BaseBusinessOrganization):
    contactPoint = ModelType(BaseContactPoint, required=True)
    address = ModelType(Address, required=True)
