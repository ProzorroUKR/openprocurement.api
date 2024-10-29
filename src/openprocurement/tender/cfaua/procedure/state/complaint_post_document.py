from openprocurement.tender.core.procedure.state.complaint_post_document import (
    ComplaintPostDocumentState,
)


class CFAUAComplaintPostDocumentState(ComplaintPostDocumentState):
    check_edrpou_confidentiality = False
