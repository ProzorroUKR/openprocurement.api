from uuid import uuid4
from schematics.types import MD5Type, StringType, BaseType, BooleanType
from schematics.types.compound import DictType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request, get_now
from openprocurement.api.models import (
    Model,
    ModelType,
    IsoDateTimeType,
    ListType,
    RootModel,
)
from openprocurement.framework.core.procedure.models.document import Document


class PatchQualification(Model):
    documents = ListType(ModelType(Document, required=True), default=list())
    status = StringType(
        choices=[
            "pending",
            "active",
            "unsuccessful"
        ],
        default="pending",
    )


class Qualification(RootModel):
    documents = ListType(ModelType(Document, required=True), default=list())
    submissionID = StringType(required=True)
    frameworkID = StringType(required=True)
    status = StringType(
        choices=[
            "pending",
            "active",
            "unsuccessful"
        ],
        default="pending",
    )

    date = IsoDateTimeType(default=get_now)
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()

    framework_owner = StringType()
    framework_token = StringType()

    submission_owner = StringType()
    submission_token = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class CreateQualification(Model):
    @serializable(serialized_name="_id")
    def id(self):
        return uuid4().hex

    @serializable
    def doc_type(self):
        return "Qualification"

    documents = ListType(ModelType(Document, required=True), default=list())
    submissionID = StringType(required=True)
    frameworkID = StringType(required=True)
    status = StringType(choices=["pending"], default="pending")
    date = IsoDateTimeType(default=get_now)
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()

    framework_owner = StringType()
    framework_token = StringType()

    submission_owner = StringType()
    submission_token = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class QualificationConfig(Model):
    test = BooleanType()
    restricted = BooleanType()
