from openprocurement.tender.belowthreshold.constants import STATUS4ROLE
from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)


class BTAwardComplaintDocumentState(AwardComplaintDocumentState):
    allowed_complaint_status_for_role = STATUS4ROLE
    allowed_tender_statuses = ("active.qualification", "active.awarded")
