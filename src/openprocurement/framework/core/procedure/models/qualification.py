from schematics.types import BaseType, BooleanType, IntType, StringType
from schematics.types.compound import DictType

from openprocurement.api.procedure.models.base import Model, RootModel
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)


class PatchQualification(Model):
    documents = ListType(ModelType(PostDocument, required=True), default=[])
    status = StringType(
        choices=["pending", "active", "unsuccessful"],
        default="pending",
    )


class Qualification(RootModel):
    documents = ListType(ModelType(Document, required=True), default=[])
    submissionID = StringType(required=True)
    frameworkID = StringType(required=True)
    status = StringType(
        choices=["pending", "active", "unsuccessful"],
        default="pending",
    )

    date = IsoDateTimeType(default=get_now)
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()

    framework_owner = StringType()
    framework_token = StringType()

    submission_owner = StringType()
    submission_token = StringType()

    _attachments = DictType(DictType(BaseType), default={})
    revisions = BaseType(default=list)
    config = BaseType()
    complaintPeriod = ModelType(Period)

    mode = StringType(choices=["test"])


class QualificationConfig(Model):
    test = BooleanType()
    restricted = BooleanType()
    qualificationComplainDuration = IntType(min_value=0)
