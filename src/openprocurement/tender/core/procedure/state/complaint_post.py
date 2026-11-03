from logging import getLogger

from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_complaint
from openprocurement.tender.core.procedure.models.complaint_post import CreateComplaintPost
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules

LOGGER = getLogger(__name__)


class ComplaintPostValidationsMixin(BaseState):
    def validate_complaint_status_for_posts(self, complaint):
        complaint_status = complaint.get("status")
        if complaint_status not in ["pending", "accepted"]:
            raise_operation_error(
                self.request,
                f"Can't submit or edit post in current ({complaint_status}) complaint status",
            )

    def validate_complaint_post_objection(self, complaint, post):
        for obj in complaint.get("objections", []):
            if obj["id"] == post.get("relatedObjection"):
                break
        else:
            raise_operation_error(
                self.request,
                "should be one of complaint objections id",
                status=422,
                name="relatedObjection",
            )


class ComplaintPostState(ComplaintPostValidationsMixin, TenderState):
    post_data_model = CreateComplaintPost

    # the reviewers ask, the complaint / tender owners answer
    complaint_post_reviewer_roles = ["aboveThresholdReviewers"]
    complaint_post_recipient_roles = ["complaint_owner", "tender_owner"]

    def validate_complaint_post_post_request(self):
        if self.request.authenticated_role != "aboveThresholdReviewers":
            self.validate_any_item_owner("complaint", "tender")
        self.validate_input_data(self.get_post_data_model())
        self.validate_data_documents(route_key="post_id", uid_key="id")

    def validate_complaint_post_recipient(self, post):
        author = self.request.authenticated_role
        recipient = post.get("recipient")
        if author in self.complaint_post_reviewer_roles and recipient not in self.complaint_post_recipient_roles:
            raise_operation_error(
                self.request,
                [f"Value must be one of {self.complaint_post_recipient_roles}."],
                status=422,
                name="recipient",
            )
        # complaint / tender owners: explanations have no relatedPost and recipient, answers to the reviewers have both
        if author in self.complaint_post_recipient_roles:
            if not post.get("relatedPost") and recipient:
                raise_operation_error(
                    self.request,
                    [f"Forbidden to add recipient without relatedPost for {self.complaint_post_recipient_roles}"],
                    status=422,
                    name="recipient",
                )
            elif post.get("relatedPost") and recipient not in self.complaint_post_reviewer_roles:
                raise_operation_error(
                    self.request,
                    [f"Value must be one of {self.complaint_post_reviewer_roles}."],
                    status=422,
                    name="recipient",
                )

    def validate_complaint_post_related_post(self, post):
        author = self.request.authenticated_role
        related_post = post.get("relatedPost")
        # an answer of the complaint / tender owner without relatedPost is rejected by validate_complaint_post_recipient
        if not related_post:
            return
        posts = get_complaint().get("posts", [])
        related_posts = [i for i in posts if i["id"] == related_post]
        if not related_posts:
            raise_operation_error(
                self.request,
                ["relatedPost should be one of posts."],
                status=422,
                name="relatedPost",
            )
        if any(i.get("relatedPost") == related_post for i in posts):
            raise_operation_error(
                self.request,
                ["relatedPost must be unique."],
                status=422,
                name="relatedPost",
            )
        if len(related_posts) > 1:  # never happens: ids are unique
            raise_operation_error(
                self.request,
                ["relatedPost can't be a link to more than one post."],
                status=422,
                name="relatedPost",
            )
        related = related_posts[0]
        if not related.get("recipient"):
            raise_operation_error(
                self.request,
                ["forbidden to answer to explanations"],
                status=422,
                name="relatedPost",
            )
        if author == related["author"]:
            raise_operation_error(
                self.request,
                ["relatedPost can't have the same author."],
                status=422,
                name="relatedPost",
            )
        if related.get("relatedPost"):
            raise_operation_error(
                self.request,
                ["relatedPost can't have relatedPost defined."],
                status=422,
                name="relatedPost",
            )
        if author != related["recipient"]:
            raise_operation_error(
                self.request,
                ["relatedPost invalid recipient."],
                status=422,
                name="relatedPost",
            )

    def validate_complaint_post_on_post(self, post):
        self.validate_complaint_post_recipient(post)
        self.validate_complaint_post_related_post(post)
        complaint = get_complaint()
        if not tender_created_after_2020_rules():
            raise_operation_error(self.request, "Forbidden")

        if complaint.get("type") != "complaint":
            raise_operation_error(
                self.request,
                f"Can't submit or edit post in current ({complaint.get('type')}) complaint type",
            )

        self.validate_complaint_status_for_posts(complaint)
        self.validate_complaint_post_objection(complaint, post)
