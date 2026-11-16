from typing import Literal

from pydantic import Field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)


class PostSignatory(Model):
    pass


class Signatory(Model):
    role: Literal["buyer", "supplier"] | None = None
    date: IsoDateTime = Field(default_factory=get_request_now)
