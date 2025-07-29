from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.constants import POST_SUBMIT_TIME
from openprocurement.tender.core.procedure.state.complaint_post import (
    ComplaintPostValidationsMixin,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentState


class ComplaintDocumentState(ComplaintPostValidationsMixin, BaseDocumentState):
    allowed_complaint_status_for_role = {  # copied from open.constants.STATUS4ROLE
        "complaint_owner": [
            "draft",
            "answered",
            "claim",
            "pending",
            "accepted",
            "satisfied",
        ],
        "aboveThresholdReviewers": ["pending", "accepted", "stopping"],
        "tender_owner": ["claim", "pending", "accepted", "satisfied"],
    }
    allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.pre-qualification",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
    post_submit_time = POST_SUBMIT_TIME

    def validate_document_post(self, data):
        if document := self.request.validated.get("document"):  # POST new version via PUT method
            self.validate_document_author(document)
        self.validate_tender_status()
        self.validate_lot_status()
        self.validate_complaint_status()

    def validate_document_patch(self, before, after):
        self.validate_document_author(before)
        self.validate_tender_status()
        self.validate_lot_status()
        self.validate_complaint_status()

    def validate_complaint_status(self):
        complaint = self.request.validated["complaint"]
        status = complaint.get("status")
        if status not in self.allowed_complaint_status_for_role.get(self.request.authenticated_role, []):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(
                self.request,
                f"Can't {operation} document in current ({status}) complaint status",
            )

    def validate_tender_status(self):
        tender = get_tender()
        status = tender["status"]
        if status not in self.allowed_tender_statuses:
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(
                self.request,
                f"Can't {operation} document in current ({status}) tender status",
            )

    def validate_lot_status(self):
        pass

    def validate_post_docs(self, data):
        complaint = self.request.validated["complaint"]
        if data["documentOf"] == "post":
            complaint_post = None
            for post in complaint.get("posts", []):
                if data.get("relatedItem") == post["id"]:
                    complaint_post = post
                    break
            if not complaint_post:
                raise_operation_error(
                    self.request,
                    "relatedItem should be one of complaint posts",
                    status=422,
                    name="relatedItem",
                )
            elif self.request.authenticated_role != complaint_post["author"]:
                raise_operation_error(
                    self.request,
                    "Can add document to post only by post author",
                    location="url",
                    name="role",
                )
            self.validate_complaint_status_for_posts(complaint)
            self.validate_complaint_post_review_date(complaint)
        elif self.request.authenticated_role != "aboveThresholdReviewers" and complaint["status"] in (
            "pending",
            "accepted",
        ):
            raise_operation_error(
                self.request,
                f"Can submit or edit document not related to post in current ({complaint['status']}) complaint "
                f"status for {self.request.authenticated_role}",
            )

    def document_always(self, data):
        super().document_always(data)
        self.validate_post_docs(data)
