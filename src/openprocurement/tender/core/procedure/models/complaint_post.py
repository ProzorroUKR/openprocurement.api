from uuid import uuid4

from schematics.types import StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.models.base import Model


class CreateComplaintPost(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def datePublished(self):
        return get_request_now().isoformat()

    @serializable
    def author(self):
        return self.get_author()

    @staticmethod
    def get_author():
        return get_request().authenticated_role

    title = StringType(required=True)
    description = StringType(required=True)
    recipient = StringType(choices=["complaint_owner", "tender_owner", "aboveThresholdReviewers"])
    relatedPost = StringType()
    relatedObjection = StringType(required=True)
