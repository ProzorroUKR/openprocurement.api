from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneCodes,
)
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardMilestoneState,
)


class BelowThresholdAwardMilestoneState(AwardMilestoneState):
    allowed_milestone_codes = (AwardMilestoneCodes.CODE_24_HOURS.value,)
