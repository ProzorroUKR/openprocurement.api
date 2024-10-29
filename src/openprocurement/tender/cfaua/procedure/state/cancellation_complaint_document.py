from openprocurement.tender.openua.procedure.state.complaint_document import (
    OpenUAComplaintDocumentState,
)


class CFAUACancellationComplaintDocumentState(OpenUAComplaintDocumentState):
    check_edrpou_confidentiality = False
