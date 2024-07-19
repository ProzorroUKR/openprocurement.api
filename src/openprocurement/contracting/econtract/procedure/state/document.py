from openprocurement.api.constants import CONFIDENTIALLY_DOCS_CAUSES
from openprocurement.api.procedure.context import get_tender
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class EContractDocumentState(BaseDocumentStateMixing, EContractState):
    def validate_document_post(self, data):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def document_on_post(self, data):
        super().document_on_post(data)
        self.set_confidentiality(data)

    def set_confidentiality(self, data):
        tender = get_tender()
        if (
            data.get("documentOf") in ("contract", "change")
            and data.get("documentType") in ("contractSigned", "contractAnnexe")
            and tender.get("cause") in CONFIDENTIALLY_DOCS_CAUSES
        ):
            data["confidentiality"] = "buyerOnly"
        else:
            data["confidentiality"] = "public"

    def validate_document_patch(self, before, after):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def document_on_patch(self, before, after):
        super().document_on_patch(before, after)
        self.set_confidentiality(after)
