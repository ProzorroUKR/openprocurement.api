from openprocurement.tender.core.procedure.state.award_document import (
    AwardDocumentState,
)


class CFAUAAwardDocumentState(AwardDocumentState):
    all_documents_should_be_public = True
