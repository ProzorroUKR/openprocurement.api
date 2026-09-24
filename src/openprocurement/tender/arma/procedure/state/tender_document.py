from openprocurement.tender.openua.procedure.state.tender_document import (
    UATenderDocumentState,
)


class TenderDocumentState(UATenderDocumentState):
    document_operation_allowed_tender_statuses = ("draft", "active.tendering", "active.pre-qualification")
    pass
