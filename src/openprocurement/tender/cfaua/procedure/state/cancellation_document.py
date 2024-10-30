from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentState,
)


class CFAUACancellationDocumentState(CancellationDocumentState):
    all_documents_should_be_public = True
