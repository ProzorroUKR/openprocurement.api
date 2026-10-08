from openprocurement.tender.core.procedure.state.award_document import (
    AwardDocumentState,
)


class ARMAAwardDocumentState(AwardDocumentState):
    award_document_allowed_tender_statuses = ("active.qualification", "active.awarded")
