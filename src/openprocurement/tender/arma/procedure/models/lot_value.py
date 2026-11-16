from typing import Literal

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.tender.core.procedure.models.value import AmountPercentageWeightedValue


class ARMAPostLotValue(Model):
    status: Literal["pending"] = "pending"
    value: AmountPercentageValue
    relatedLot: MD5
    subcontractingDetails: str | None = None


class ARMAPatchLotValue(ARMAPostLotValue):
    weightedValue: AmountPercentageWeightedValue | None = None
    status: Literal["pending", "active", "unsuccessful"] = "pending"
    date: str | None = None


class ARMALotValue(ARMAPatchLotValue):
    initialValue: AmountPercentageValue | None = None
    participationUrl: str | None = None
