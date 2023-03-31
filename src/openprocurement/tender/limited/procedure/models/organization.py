from openprocurement.tender.limited.constants import REPORTING_KINDS, NEGOTIATION_KINDS
from openprocurement.api.models import ModelType
from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
    Organization,
    Identifier,
    Address,
    ContactPoint,
)
from schematics.types import StringType


class ReportingProcuringEntity(BaseProcuringEntity):
    contactPoint = ModelType(ContactPoint)
    kind = StringType(choices=REPORTING_KINDS, required=True)


class NegotiationProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=NEGOTIATION_KINDS, required=True)


class ReportFundOrganization(Organization):
    identifier = ModelType(Identifier)  # not required
    address = ModelType(Address)  # not required
    contactPoint = ModelType(ContactPoint)  # not required
