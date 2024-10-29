from openprocurement.tender.open.procedure.state.tender_document import (
    UATenderDocumentState,
)


class CFAUATenderDocumentState(UATenderDocumentState):
    check_edrpou_confidentiality = False
