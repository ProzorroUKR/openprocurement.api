from typing import Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import MD5, IsoDateTime


class BaseCancellation(Model):
    reason: str = Field(min_length=1)
    reason_en: str | None = None
    status: Literal["pending", "active"] = "pending"


class PostCancellation(BaseCancellation):
    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def date(self) -> str:
        return get_request_now().isoformat()


class PatchCancellation(BaseCancellation):
    pass


class Cancellation(BaseCancellation):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    date: IsoDateTime = Field(default_factory=get_request_now)
