from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintState
from openprocurement.tender.core.procedure.context import get_tender


class CFAUAAwardComplaintState(AwardComplaintState):
    create_allowed_tender_statuses = ("active.qualification.stand-still",)
    update_allowed_tender_statuses = ("active.qualification.stand-still", "active.qualification")

    def reviewers_satisfied_handler(self, complaint):
        super().reviewers_satisfied_handler(complaint)
        tender = get_tender()
        if "endDate" in tender.get("qualificationPeriod", ""):
            del tender["qualificationPeriod"]["endDate"]
        self.get_change_tender_status_handler("active.qualification")(tender)
