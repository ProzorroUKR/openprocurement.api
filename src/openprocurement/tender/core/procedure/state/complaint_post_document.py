from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.context import get_complaint, get_post
from openprocurement.tender.core.procedure.state.complaint_post import ComplaintPostValidationsMixin
from openprocurement.tender.core.constants import POST_SUBMIT_TIME
from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.utils import raise_operation_error


class ComplaintPostDocumentState(ComplaintPostValidationsMixin, BaseDocumentState):
    calendar = WORKING_DAYS
    post_submit_time = POST_SUBMIT_TIME

    def validate_document_post(self, data):
        if document := self.request.validated.get("document"):  # POST new version via PUT method
            self.validate_document_author(document)
        else:
            post = get_post()
            if self.request.authenticated_role != post["author"]:
                raise_operation_error(
                    self.request,
                    "Can add document only by post author",
                    location="url",
                    name="role",
                )
        complaint = get_complaint()
        self.validate_complaint_status(complaint)
        self.validate_complaint_post_review_date(complaint)

    def validate_document_patch(self, before, after):
        self.validate_document_author(before)
        complaint = get_complaint()
        self.validate_complaint_status(complaint)
        self.validate_complaint_post_review_date(complaint)
