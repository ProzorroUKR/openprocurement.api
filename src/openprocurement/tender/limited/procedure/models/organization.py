from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import Organization
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.organization import (
    Address,
    ContactPoint,
)
from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)


class ReportingProcuringEntity(BaseProcuringEntity):
    contactPoint = ModelType(ContactPoint)


class ReportFundOrganization(Organization):
    identifier = ModelType(Identifier)  # not required
    address = ModelType(Address)  # not required
    contactPoint = ModelType(ContactPoint)  # not required
