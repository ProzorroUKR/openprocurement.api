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

    def validate_post_request(self):
        if self.request.authenticated_role != "aboveThresholdReviewers":
            self.validate_any_item_owner("complaint", "tender")
        self.validate_input_data(self.get_post_data_model())
        self.validate_data_documents(route_key="post_id", uid_key="id")

    def validate_complaint_post_on_post(self, post):
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
