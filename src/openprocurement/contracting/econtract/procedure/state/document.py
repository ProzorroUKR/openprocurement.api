from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class EContractDocumentState(BaseDocumentStateMixing, EContractState):
    def validate_document_post(self, data):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def validate_document_patch(self, before, after):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))
