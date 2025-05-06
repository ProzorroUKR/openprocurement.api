from datetime import timedelta
from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.framework.core.utils import calculate_framework_full_date

CONTRACT_BAN_DURATION = 90


class PostMilestone(Model):
    @serializable
    def id(self):
        return uuid4().hex

    type = StringType(required=True, choices=["activation", "ban"])
    documents = ListType(ModelType(PostDocument, required=True), default=[])
    status = StringType(choices=["scheduled"], default="scheduled")

    @serializable(serialized_name="dueDate", serialize_when_none=False)
    def milestone_dueDate(self):
        if self.type == "ban":
            due_date = calculate_framework_full_date(
                get_request_now(),
                timedelta(days=CONTRACT_BAN_DURATION),
                framework=get_framework(),
                ceil=True,
            )
            return due_date.isoformat()
        return None


class PatchMilestone(Model):
    status = StringType(choices=["scheduled", "met", "notMet", "partiallyMet"])
    documents = ListType(ModelType(PostDocument, required=True))


class Milestone(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    type = StringType(required=True, choices=["activation", "ban"])
    status = StringType(choices=["scheduled", "met", "notMet", "partiallyMet"], default="scheduled")
    dueDate = IsoDateTimeType()
    documents = ListType(ModelType(Document, required=True), default=[])
    dateModified = IsoDateTimeType(default=get_request_now)
    dateMet = IsoDateTimeType()
