from openprocurement.tender.limited.constants import REPORTING_KINDS, NEGOTIATION_KINDS
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity as BaseProcuringEntity
from schematics.types import StringType


class ReportingProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=REPORTING_KINDS, required=True)


class NegotiationProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=NEGOTIATION_KINDS, required=True)
