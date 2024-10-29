from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentState,
)


class CFAUACancellationDocumentState(CancellationDocumentState):
    check_edrpou_confidentiality = False
