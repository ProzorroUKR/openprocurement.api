from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class AboveThresholdTenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True


class AboveThresholdUATenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True


class COTenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True


class BelowThresholdTenderDocumentState(TenderDocumentState):
    document_operation_allowed_tender_statuses = ("draft", "active.enquiries")
    document_operation_allowed_tender_statuses_for_funder = ("active.tendering",)
    invalidate_bids_on_document_change = True


class RFPTenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True
