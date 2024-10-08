from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.planning.api.constants import (
    MILESTONE_APPROVAL_DESCRIPTION,
    MILESTONE_APPROVAL_TITLE,
)
from openprocurement.planning.api.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.planning.api.procedure.models.organization import BaseOrganization


class BaseMilestone(Model):
    TYPE_APPROVAL = "approval"

    STATUS_SCHEDULED = "scheduled"
    STATUS_MET = "met"
    STATUS_NOT_MET = "notMet"
    STATUS_INVALID = "invalid"

    TYPE_CHOICES = (TYPE_APPROVAL,)
    STATUS_CHOICES = (
        STATUS_SCHEDULED,
        STATUS_MET,
        STATUS_NOT_MET,
        STATUS_INVALID,
    )

    ACTIVE_STATUSES = (
        STATUS_SCHEDULED,
        STATUS_MET,
    )


class PostMilestone(BaseMilestone):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def dateModified(self):
        return get_now().isoformat()

    status = StringType(
        required=True,
        choices=BaseMilestone.STATUS_CHOICES,
        default=BaseMilestone.STATUS_SCHEDULED,
    )
    dueDate = IsoDateTimeType(required=True)
    title = StringType(required=True, choices=[MILESTONE_APPROVAL_TITLE])
    description = StringType(required=True, min_length=3, default=MILESTONE_APPROVAL_DESCRIPTION)
    type = StringType(required=True, choices=[BaseMilestone.TYPE_APPROVAL])
    documents = ListType(ModelType(PostDocument, required=True))
    author = ModelType(BaseOrganization, required=True)


class PatchMilestone(BaseMilestone):
    status = StringType(choices=BaseMilestone.STATUS_CHOICES)
    dueDate = IsoDateTimeType()
    description = StringType(min_length=3)


class Milestone(BaseMilestone):
    id = MD5Type(required=True)
    status = StringType(required=True, choices=BaseMilestone.STATUS_CHOICES)
    title = StringType(required=True, choices=[MILESTONE_APPROVAL_TITLE])
    description = StringType(required=True, min_length=3)
    type = StringType(required=True, choices=[BaseMilestone.TYPE_APPROVAL])
    dueDate = IsoDateTimeType(required=True)
    documents = ListType(ModelType(Document, required=True))
    author = ModelType(BaseOrganization, required=True)
    dateModified = IsoDateTimeType()
    dateMet = IsoDateTimeType()
    owner = StringType()
    owner_token = StringType()
