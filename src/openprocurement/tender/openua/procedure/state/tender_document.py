from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class UATenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True
