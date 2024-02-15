from schematics.types import StringType

from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD_KINDS
from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=BELOW_THRESHOLD_KINDS, required=True)
