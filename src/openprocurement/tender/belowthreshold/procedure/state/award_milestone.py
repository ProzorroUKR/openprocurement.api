from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneCode,
)
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardMilestoneState,
)


class BelowThresholdAwardMilestoneState(AwardMilestoneState):
    allowed_milestone_codes = (AwardMilestoneCode.CODE_24_HOURS.value,)
