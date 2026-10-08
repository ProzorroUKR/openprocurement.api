from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class CFASelectionTenderDocumentState(TenderDocumentState):
    document_operation_allowed_tender_statuses = ("draft", "draft.pending", "active.enquiries")
    all_documents_should_be_public = True
