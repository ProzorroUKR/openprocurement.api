from typing import Any
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.constants import PERIOD_CHANGE_CAUSES, PeriodChangeCause
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)


class Modifications(Model):
    qualificationPeriod: PeriodEndRequired | None = None


class PostChange(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    rationale: str = Field(min_length=1)
    rationale_en: str | None = None
    rationaleType: PeriodChangeCause
    modifications: Modifications
    documents: list[PostDocument] = []

    @model_field_validator("rationale")
    def validate_rationale(self, value):
        if self.rationaleType != "other" and value != PERIOD_CHANGE_CAUSES.get(self.rationaleType):
            raise ValidationError("Value should be from dictionary `framework_period_change_causes`.")


class Change(Model):
    id: MD5 | None = None
    date: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    rationale: str = Field(min_length=1)
    rationale_en: str | None = None
    rationaleType: PeriodChangeCause
    modifications: Modifications
    previous: Modifications
    documents: list[Document] | None = None
