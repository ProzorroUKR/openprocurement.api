from openprocurement.tender.core.procedure.state.document import BaseDocumentState


class TenderDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        pass

    def validate_document_patch(self, before, after):
        pass
