from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class COTenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True
