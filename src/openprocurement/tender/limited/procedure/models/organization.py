from schematics.types import StringType

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
from openprocurement.tender.limited.constants import NEGOTIATION_KINDS, REPORTING_KINDS


class ReportingProcuringEntity(BaseProcuringEntity):
    contactPoint = ModelType(ContactPoint)
    kind = StringType(choices=REPORTING_KINDS, required=True)


class NegotiationProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=NEGOTIATION_KINDS, required=True)


class ReportFundOrganization(Organization):
    identifier = ModelType(Identifier)  # not required
    address = ModelType(Address)  # not required
    contactPoint = ModelType(ContactPoint)  # not required
