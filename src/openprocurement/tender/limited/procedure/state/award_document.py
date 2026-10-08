from openprocurement.tender.core.procedure.state.award_document import (
    AwardDocumentState,
)


class LimitedAwardDocumentState(AwardDocumentState):
    award_document_allowed_tender_statuses = ("active",)
    award_document_bots_extra_statuses = ()
    award_document_lot_check = False
    award_document_author_check = False
    award_document_post_requires_pending_award = True
