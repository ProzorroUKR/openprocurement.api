from schematics.types import StringType

from openprocurement.tender.esco.constants import ESCO_KINDS
from openprocurement.tender.openeu.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=ESCO_KINDS, required=True)
