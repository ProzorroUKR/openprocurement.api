from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardMilestoneState,
)


class ReportingAwardMilestoneState(AwardMilestoneState):
    allowed_milestone_codes = ()
