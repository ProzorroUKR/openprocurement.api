from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTime
from openprocurement.api.utils import get_now


class PostTransfer(Model):
    @computed_field(alias="_id")
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def date(self) -> str:
        return get_now().isoformat()


class PatchTransfer(Model):
    pass


class Transfer(Model):
    owner: str | None = Field(None, min_length=1)
    access_token: str = Field(min_length=1)
    transfer_token: str = Field(min_length=1)
    date: IsoDateTime
    usedFor: str | None = Field(None, min_length=32)  # object path (e.g. /tenders/{id})
