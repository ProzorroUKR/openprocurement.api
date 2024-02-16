from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.tender import TenderState


class BaseDocumentStateMixing:
    def document_on_post(self, data):
        self.validate_document_post(data)

    def document_on_patch(self, before, after):
        self.validate_document_patch(before, after)

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
