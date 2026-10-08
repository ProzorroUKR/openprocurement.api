from openprocurement.tender.core.procedure.state.award_document import (
    AwardDocumentState,
)


class CFAUAAwardDocumentState(AwardDocumentState):
    award_document_post_bots_extra_statuses = ("active.awarded", "active.qualification.stand-still")
    award_document_forbidden_with_accepted_lot_complaint = True
    all_documents_should_be_public = True
