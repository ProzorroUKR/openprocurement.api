from openprocurement.tender.open.procedure.state.tender_document import (
    UATenderDocumentState,
)


class CFAUATenderDocumentState(UATenderDocumentState):
    all_documents_should_be_public = True
