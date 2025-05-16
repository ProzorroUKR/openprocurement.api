from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_appeal
from openprocurement.tender.core.procedure.state.complaint_appeal import (
    ComplaintAppealValidationsMixin,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentState


class ComplaintAppealDocumentState(ComplaintAppealValidationsMixin, BaseDocumentState):
    def validate_document_post(self, data):
        if document := self.request.validated.get("document"):  # POST new version via PUT method
            self.validate_document_author(document)
        else:
            appeal = get_appeal()
            if self.request.authenticated_role != appeal["author"]:
                raise_operation_error(
                    self.request,
                    "Appeal document can be added only by appeal author",
                    location="url",
                    name="role",
                )
        self.appeal_always()

    def validate_document_patch(self, before, after):
        self.validate_document_author(before)
        self.appeal_always()
