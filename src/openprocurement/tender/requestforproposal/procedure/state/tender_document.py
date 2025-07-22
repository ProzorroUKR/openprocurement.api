from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class RequestForProposalTenderDocumentState(TenderDocumentState):
    def document_on_post(self, data):
        super().document_on_post(data)
        self.invalidate_bids_data(get_tender())

    def document_on_patch(self, before, after):
        super().document_on_patch(before, after)
        self.invalidate_bids_data(get_tender())
