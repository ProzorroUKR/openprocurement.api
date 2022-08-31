from openprocurement.tender.core.procedure.models.organization import ProcuringEntity as BaseProcuringEntity
from openprocurement.tender.open.constants import UA_KINDS
from schematics.types import StringType


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=UA_KINDS, required=True)
