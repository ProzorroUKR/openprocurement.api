from openprocurement.tender.core.procedure.state.bid_document import (
    BidDocumentState,
    BidFinancialDocumentState,
)


class CFAUABidDocumentState(BidDocumentState):
    bid_document_allowed_tender_statuses = (
        "active.tendering",
        "active.qualification",
        "active.awarded",
        "active.qualification.stand-still",
    )


class CFAUABidFinancialDocumentState(BidFinancialDocumentState):
    bid_document_allowed_tender_statuses = CFAUABidDocumentState.bid_document_allowed_tender_statuses
