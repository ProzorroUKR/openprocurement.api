from openprocurement.tender.core.procedure.models.organization import ProcuringEntity as BaseProcuringEntity
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD_KINDS
from schematics.types import StringType


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=BELOW_THRESHOLD_KINDS, required=True)
