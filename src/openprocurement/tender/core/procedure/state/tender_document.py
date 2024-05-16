from openprocurement.tender.core.procedure.state.document import BaseDocumentState


class TenderDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        self.validate_action_with_exist_inspector_review_request()

    def validate_document_patch(self, before, after):
        self.validate_action_with_exist_inspector_review_request()
