from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)


class BaseDocumentStateMixing:
    check_edrpou_confidentiality = True
    all_documents_should_be_public = False

    def document_on_post(self, data):
        self.validate_document_post(data)
        self.document_always(data)

    def document_on_patch(self, before, after):
        self.validate_document_patch(before, after)
        self.document_always(after)

    def document_always(self, data):
        pass

    def validate_confidentiality(self, data):
        if not self.check_edrpou_confidentiality:
            return
        validate_edrpou_confidentiality_doc(data, should_be_public=self.all_documents_should_be_public)

    def validate_document_post(self, data):
        pass

    def validate_document_patch(self, before, after):
        pass


class BaseDocumentState(BaseDocumentStateMixing, TenderState):
    def validate_document_author(self, document):
        if self.request.authenticated_role != document["author"]:
            raise_operation_error(
                self.request,
                "Can update document only author",
                location="url",
                name="role",
            )

    def document_always(self, data):
        self.invalidate_review_requests()
        self.validate_confidentiality(data)
