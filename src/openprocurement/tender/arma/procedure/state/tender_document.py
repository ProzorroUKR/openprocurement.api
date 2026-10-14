from openprocurement.tender.core.procedure.state.tender_document import TenderDocumentState


class ARMATenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True


class ComplexAssetTenderDocumentState(ARMATenderDocumentState):
    document_operation_allowed_tender_statuses = ("draft", "active.tendering", "active.pre-qualification")


class SimpleAssetTenderDocumentState(ARMATenderDocumentState):
    document_operation_allowed_tender_statuses = ("draft", "active.tendering")
