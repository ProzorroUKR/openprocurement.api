from schematics.types import StringType

from openprocurement.tender.competitiveordering.constants import UA_KINDS
from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=UA_KINDS, required=True)
