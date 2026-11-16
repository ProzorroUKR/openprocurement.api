from typing import Literal

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.tender.core.procedure.models.value import (
    WeightedValue,
)


class PostLotValue(Model):
    status: Literal["pending"] = "pending"
    value: Value
    relatedLot: MD5
    subcontractingDetails: str | None = None


class PatchLotValue(PostLotValue):
    weightedValue: WeightedValue | None = None
    status: Literal["pending", "active", "unsuccessful"] = "pending"
    date: str | None = None


class LotValue(PatchLotValue):
    initialValue: Value | None = None
    participationUrl: str | None = None
