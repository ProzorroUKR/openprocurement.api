from typing import Any, Literal

from pydantic import Field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import (
    IsoDateTime,
)
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.base import FrameworkRootModel
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)


class PatchQualification(Model):
    documents: list[PostDocument] | None = None
    status: Literal["pending", "active", "unsuccessful"] | None = None


class Qualification(FrameworkRootModel):
    documents: list[Document] = []
    submissionID: str
    frameworkID: str
    status: Literal["pending", "active", "unsuccessful"] = "pending"
    date: IsoDateTime = Field(default_factory=get_now)
    dateCreated: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    framework_owner: str | None = None
    framework_token: str | None = None
    submission_owner: str | None = None
    submission_token: str | None = None
    attachments_: dict[str, Any] = Field(default_factory=dict, alias="_attachments")
    config: Any = None
    complaintPeriod: Period | None = None
    mode: Literal["test"] | None = None


class QualificationConfig(Model):
    test: bool | None = None
    restricted: bool | None = None
    qualificationComplainDuration: int | None = Field(None, ge=0)
