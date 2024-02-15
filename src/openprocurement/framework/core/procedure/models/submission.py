from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types import StringType, BaseType, BooleanType
from schematics.types.compound import DictType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.base import Model, RootModel
from openprocurement.api.procedure.types import ListType, ModelType, IsoDateTimeType
from openprocurement.api.utils import get_now, get_framework_by_id
from openprocurement.framework.core.procedure.models.document import Document
from openprocurement.framework.core.procedure.models.organization import (
    SubmissionBusinessOrganization,
)
from openprocurement.framework.dps.constants import DPS_TYPE


class PostSubmission(Model):
    @serializable(serialized_name="_id")
    def id(self):
        return uuid4().hex

    @serializable
    def doc_type(self):
        return "Submission"

    tenderers = ListType(ModelType(SubmissionBusinessOrganization, required=True), required=True, min_size=1)
    documents = ListType(ModelType(Document, required=True), default=list())
    frameworkID = StringType(required=True)
    status = StringType(choices=["draft"], default="draft")

    def validate_frameworkID(self, data, value):
        framework = get_framework_by_id(get_request(), value, raise_error=False)
        if not framework:
            raise ValidationError("frameworkID must be one of exists frameworks")


class PatchSubmission(Model):
    tenderers = ListType(ModelType(SubmissionBusinessOrganization, required=True), min_size=1)
    frameworkID = StringType()
    status = StringType(
        choices=["draft", "active", "deleted", "complete"],
        default="draft",
    )


class PatchActiveSubmission(Model):
    pass


class BotPatchSubmission(Model):
    qualificationID = StringType()
    status = StringType(
        choices=["draft", "active", "deleted", "complete"],
        default="draft",
    )


class Submission(RootModel):
    tenderers = ListType(ModelType(SubmissionBusinessOrganization, required=True), required=True, min_size=1)
    documents = ListType(ModelType(Document, required=True), default=list())
    qualificationID = StringType()
    frameworkID = StringType(required=True)
    status = StringType(
        choices=["draft", "active", "deleted", "complete"],
        default="draft",
    )

    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType(default=get_now)
    datePublished = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()

    framework_owner = StringType()
    framework_token = StringType()

    transfer_token = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])


class SubmissionConfig(Model):
    test = BooleanType()
    restricted = BooleanType()

    def validate_restricted(self, data, value):
        framework = get_request().validated.get("framework")
        if not framework:
            return
        if framework.get("frameworkType") == DPS_TYPE:
            if value is None:
                raise ValidationError("restricted is required for this framework type")
            if framework.get("procuringEntity", {}).get("kind") == "defense":
                if value is False:
                    raise ValidationError("restricted must be true for defense procuring entity")
            else:
                if value is True:
                    raise ValidationError("restricted must be false for non-defense procuring entity")
        else:
            if value is True:
                raise ValidationError("restricted must be false for this framework type")
