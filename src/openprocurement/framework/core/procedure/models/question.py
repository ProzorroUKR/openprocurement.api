from typing import Any
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.organization import Organization


class Question(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    author: Organization
    title: str
    description: str | None = None
    date: IsoDateTime | None = None
    answer: str | None = None
    dateAnswered: IsoDateTime | None = None


class PostQuestion(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_now().isoformat()

    author: Organization
    title: str
    description: str | None = None


class PatchQuestion(Model):
    answer: str
