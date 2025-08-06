from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.tender.core.procedure.context import get_complaint


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

    reviewer_roles = ["aboveThresholdReviewers"]
    recipient_roles = ["complaint_owner", "tender_owner"]

    def validate_relatedPost(self, data, value):
        complaint = get_complaint()

        author = self.get_author()
        # only for responses to AMCU post it is required to add relatedPost
        if author in self.recipient_roles and data.get("recipient") and not value:
            raise ValidationError(BaseType.MESSAGES["required"])

        if value:
            posts = complaint.get("posts", [])
            # check that another post with "id"
            # that equals "relatedPost" of current post exists
            if not any(p["id"] == value for p in posts):
                raise ValidationError("relatedPost should be one of posts.")

            # check that another posts with `relatedPost`
            # that equals `relatedPost` of current post does not exist
            if any(p.get("relatedPost") == value for p in posts):
                raise ValidationError("relatedPost must be unique.")

            related_posts = [i for i in posts if i["id"] == value]

            # check that there are no multiple related posts,
            # that should never happen coz `id` is unique
            if len(related_posts) > 1:
                raise ValidationError("relatedPost can't be a link to more than one post.")

            if not related_posts[0].get("recipient"):
                raise ValidationError("forbidden to answer to explanations")

            # check that related post have another author
            if len(related_posts) == 1 and author == related_posts[0]["author"]:
                raise ValidationError("relatedPost can't have the same author.")

            # check that related post is not an answer to another post
            if len(related_posts) == 1 and related_posts[0].get("relatedPost"):
                raise ValidationError("relatedPost can't have relatedPost defined.")

            # check that answer author matches related post recipient
            if related_posts[0].get("recipient") and author != related_posts[0]["recipient"]:
                raise ValidationError("relatedPost invalid recipient.")

    def validate_recipient(self, data, value):
        # validate for aboveThresholdReviewers role
        author = self.get_author()
        if author in self.reviewer_roles and value not in self.recipient_roles:
            raise ValidationError(f"Value must be one of {self.recipient_roles}.")

        # validate for complaint_owner and tender_owner roles for AMCU responses
        if author in self.recipient_roles:
            # explanations should not have relatedPost and recipient field
            if not data.get("relatedPost") and value:
                raise ValidationError(f"Forbidden to add recipient without relatedPost for {self.recipient_roles}")
            elif data.get("relatedPost") and value not in self.reviewer_roles:
                raise ValidationError(f"Value must be one of {self.reviewer_roles}.")
