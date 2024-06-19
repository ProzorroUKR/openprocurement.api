from openprocurement.tender.core.procedure.state.document import BaseDocumentState


class TenderDocumentState(BaseDocumentState):
    def document_always(self, data: dict) -> None:
        if data.get("documentType") != "notice":
            self.validate_action_with_exist_inspector_review_request()
        super().document_always(data)
