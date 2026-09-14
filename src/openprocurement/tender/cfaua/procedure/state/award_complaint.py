from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class CFAUAAwardComplaintState(AwardComplaintStateMixin, CFAUATenderState):
    create_allowed_tender_statuses = ("active.qualification.stand-still",)
    update_allowed_tender_statuses = (
        "active.qualification.stand-still",
        "active.qualification",
    )
    all_documents_should_be_public = True

    satisfied_complaint_returns_to_qualification = True
