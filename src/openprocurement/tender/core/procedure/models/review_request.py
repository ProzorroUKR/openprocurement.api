from schematics.types import StringType, BooleanType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class PostInspectorReview(Model):
    lotID = StringType()


class PatchInspectorReviewRequest(Model):
    approved = BooleanType(required=True)
    description = StringType()


class ReviewRequest(Model):
    id = StringType()
    lotID = StringType()
    tenderStatus = StringType(required=True)
    approved = BooleanType()
    description = StringType()
    dateCreated = IsoDateTimeType(required=True)
    date = IsoDateTimeType()
