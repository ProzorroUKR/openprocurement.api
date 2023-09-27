from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.tender_document import TenderDocumentState


class PQDocumentState(TenderDocumentState):
    def document_on_post(self, data: dict) -> None:
        super().document_on_post(data)
        self.update_tender_template(data)

    def update_tender_template(self, data: dict) -> None:
        tender = get_tender()
        if "contractTemplateName" in tender and data.get("documentType", "") == "contractProforma":
            del tender["contractTemplateName"]
