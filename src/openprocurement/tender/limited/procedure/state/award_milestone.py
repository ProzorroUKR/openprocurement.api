from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardMilestoneState,
)


class ReportingAwardMilestoneState(AwardMilestoneState):
    allowed_milestone_codes = ()
    milestone_post_allowed_tender_statuses = ("active",)
    milestone_post_requires_active_lot = False
