from openprocurement.tender.core.procedure.state.tender_document import (
    TenderDocumentState,
)


class CFASelectionTenderDocumentState(TenderDocumentState):
    check_edrpou_confidentiality = False
