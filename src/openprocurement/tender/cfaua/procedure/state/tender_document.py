from openprocurement.tender.core.procedure.state.tender_document import TenderDocumentState


class CFAUATenderDocumentState(TenderDocumentState):
    invalidate_bids_on_document_change = True
    all_documents_should_be_public = True
