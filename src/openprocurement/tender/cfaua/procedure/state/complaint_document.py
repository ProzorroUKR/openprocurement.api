from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


class CFAUAComplaintDocumentState(OpenComplaintDocumentState):
    check_edrpou_confidentiality = False
