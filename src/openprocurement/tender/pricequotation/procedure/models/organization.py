from openprocurement.tender.pricequotation.constants import PQ_KINDS
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity as BaseProcuringEntity
from schematics.types import StringType


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=PQ_KINDS, required=True)

