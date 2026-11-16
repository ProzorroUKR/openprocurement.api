from pydantic import Field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTime


class RationaleObject(Model):
    description: str = Field(max_length=2048)
    date: IsoDateTime | None = None
