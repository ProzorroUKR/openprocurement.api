from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class CFAUAAwardComplaintState(AwardComplaintStateMixin, CFAUATenderState):
    create_allowed_tender_statuses = ("active.qualification.stand-still",)
    update_allowed_tender_statuses = ("active.qualification.stand-still", "active.qualification")

    def reviewers_satisfied_handler(self, complaint):
        super().reviewers_satisfied_handler(complaint)
        tender = get_tender()
        tender["awardPeriod"].pop("endDate", None)
        self.get_change_tender_status_handler("active.qualification")(tender)
