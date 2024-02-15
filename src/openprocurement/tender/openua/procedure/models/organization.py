from schematics.types import StringType

from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)
from openprocurement.tender.openua.constants import UA_KINDS


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=UA_KINDS, required=True)
