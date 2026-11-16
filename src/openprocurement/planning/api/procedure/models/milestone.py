from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import MD5, IsoDateTime
from openprocurement.planning.api.constants import (
    MILESTONE_APPROVAL_DESCRIPTION,
    MilestoneStatus,
    MilestoneTitle,
    MilestoneType,
)
from openprocurement.planning.api.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.planning.api.procedure.models.organization import BaseOrganization


class BaseMilestone(Model):
    pass


class PostMilestone(BaseMilestone):
    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def dateModified(self) -> str:
        return get_request_now().isoformat()

    status: MilestoneStatus = MilestoneStatus.SCHEDULED
    dueDate: IsoDateTime
    title: MilestoneTitle
    description: str = Field(MILESTONE_APPROVAL_DESCRIPTION, min_length=3)
    type: MilestoneType
    documents: list[PostDocument] | None = None
    author: BaseOrganization


class PatchMilestone(BaseMilestone):
    status: MilestoneStatus | None = None
    dueDate: IsoDateTime | None = None
    description: str | None = Field(None, min_length=3)


class Milestone(BaseMilestone):
    id: MD5
    status: MilestoneStatus
    title: MilestoneTitle
    description: str = Field(min_length=3)
    type: MilestoneType
    dueDate: IsoDateTime
    documents: list[Document] | None = None
    author: BaseOrganization
    dateModified: IsoDateTime | None = None
    dateMet: IsoDateTime | None = None
    owner: str | None = None
    owner_token: str | None = None
