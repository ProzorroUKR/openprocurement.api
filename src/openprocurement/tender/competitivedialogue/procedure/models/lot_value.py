from typing import Literal

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
)


class CDPatchLotValue(Model):
    relatedLot: MD5 | None = None
    subcontractingDetails: str | None = None
    status: Literal["pending", "active", "unsuccessful"] = "pending"
    date: str | None = None


class CDLotValue(CDPatchLotValue):
    initialValue: Value | None = None
    participationUrl: str | None = None


class CDPostLotValue(Model):
    relatedLot: MD5 | None = None
    subcontractingDetails: str | None = None
    status: Literal["pending"] = "pending"
