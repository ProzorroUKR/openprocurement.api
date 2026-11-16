from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)


class QualificationMilestoneCode(StrEnum):
    CODE_24_HOURS = "24h"
    CODE_LOW_PRICE = "alp"


class PostQualificationMilestone(Model):
    code: Literal[QualificationMilestoneCode.CODE_24_HOURS]
    description: str | None = None
    dueDate: IsoDateTime | None = None

    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_request_now().isoformat()
