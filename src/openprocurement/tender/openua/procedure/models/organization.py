from schematics.types import StringType

from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)
from openprocurement.tender.openua.constants import UA_PROCURING_ENTITY_KIND_CHOICES


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=UA_PROCURING_ENTITY_KIND_CHOICES, required=True)
