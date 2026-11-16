from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.base import FrameworkRootModel
from openprocurement.framework.core.procedure.models.organization import (
    SubmissionBusinessOrganization,
)
from openprocurement.framework.core.procedure.models.submission_document import (
    PostSubmissionDocument,
    SubmissionDocument,
)


class PostSubmission(Model):
    @computed_field(alias="_id")
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def doc_type(self) -> Any:
        return "Submission"

    tenderers: list[SubmissionBusinessOrganization] = Field(min_length=1)
    documents: list[PostSubmissionDocument] = []
    frameworkID: str
    status: Literal["draft"] = "draft"


class PatchSubmission(Model):
    tenderers: list[SubmissionBusinessOrganization] | None = Field(None, min_length=1)
    frameworkID: str | None = None
    status: Literal["draft", "active", "deleted", "complete"] | None = None


class PatchActiveSubmission(Model):
    pass


class BotPatchSubmission(Model):
    qualificationID: str | None = None
    status: Literal["draft", "active", "deleted", "complete"] | None = None


class Submission(FrameworkRootModel):
    tenderers: list[SubmissionBusinessOrganization] = Field(min_length=1)
    documents: list[SubmissionDocument] = []
    qualificationID: str | None = None
    frameworkID: str
    status: Literal["draft", "active", "deleted", "complete"] = "draft"
    dateCreated: IsoDateTime | None = None
    dateModified: IsoDateTime | None = None
    date: IsoDateTime = Field(default_factory=get_now)
    datePublished: IsoDateTime | None = None
    owner: str | None = None
    owner_token: str | None = None
    framework_owner: str | None = None
    framework_token: str | None = None
    transfer_token: str | None = None
    attachments_: dict[str, Any] = Field(default_factory=dict, alias="_attachments")
    config: Any = None
    mode: Literal["test"] | None = None
