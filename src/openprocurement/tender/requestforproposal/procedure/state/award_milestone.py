from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneCode,
)
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardMilestoneState,
)


class RequestForProposalAwardMilestoneState(AwardMilestoneState):
    allowed_milestone_codes = (AwardMilestoneCode.CODE_24_HOURS.value,)

    def get_24h_milestone_dueDate(self, milestone):
        # if user selected dueDate > 24h, then accept it. Else set dueDate at 24h
        min_dueDate = super().get_24h_milestone_dueDate(milestone)
        milestone_dueDate = milestone.get("dueDate", min_dueDate)
        return max(min_dueDate, milestone_dueDate)
