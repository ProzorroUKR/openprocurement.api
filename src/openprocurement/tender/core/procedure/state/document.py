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
    pass
