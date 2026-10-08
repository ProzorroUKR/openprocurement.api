from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class LimitedTenderDocumentState(TenderDocumentState):
    document_operation_allowed_tender_statuses = ("draft", "active")
    document_operation_auction_role_statuses = None
    document_operation_sign_docs_extra_statuses = ()
