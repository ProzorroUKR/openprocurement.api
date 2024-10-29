from openprocurement.tender.core.procedure.state.award_document import (
    AwardDocumentState,
)


class CFAUAAwardDocumentState(AwardDocumentState):
    check_edrpou_confidentiality = False
