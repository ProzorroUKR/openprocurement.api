from datetime import timedelta
from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.framework.core.utils import calculate_framework_full_date

CONTRACT_BAN_DURATION = 90


class PostMilestone(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    type: Literal["activation", "ban"]
    documents: list[PostDocument] = []
    status: Literal["scheduled"] = "scheduled"

    @computed_field
    def dueDate(self) -> Any:
        if self.type == "ban":
            due_date = calculate_framework_full_date(
                get_request_now(), timedelta(days=CONTRACT_BAN_DURATION), framework=get_framework(), ceil=True
            )
            return due_date.isoformat()
        return None


class PatchMilestone(Model):
    status: Literal["scheduled", "met", "notMet", "partiallyMet"] | None = None
    documents: list[PostDocument] | None = None


class Milestone(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    type: Literal["activation", "ban"]
    status: Literal["scheduled", "met", "notMet", "partiallyMet"] = "scheduled"
    dueDate: IsoDateTime | None = None
    documents: list[Document] = []
    dateModified: IsoDateTime = Field(default_factory=get_request_now)
    dateMet: IsoDateTime | None = None
