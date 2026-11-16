from typing import Any, Literal
from uuid import uuid4

from pydantic import computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)


class PostCancellation(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def dateCreated(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def status(self) -> Any:
        return "pending"

    reason: str
    reasonType: Literal["requiresChanges"]


class PostContractCancellation(PostCancellation):
    reasonType: Literal["requiresChanges", "signingRefusal"]


class Cancellation(Model):
    id: MD5
    status: Literal["pending", "active"]
    reason: str
    reasonType: Literal["requiresChanges", "signingRefusal"]
    dateCreated: IsoDateTime
    author: str | None = None
