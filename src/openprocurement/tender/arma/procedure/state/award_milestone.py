from openprocurement.tender.arma.procedure.models.award_milestone import ARMAPostAwardMilestone
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
)


class ARMAAwardMilestoneState(AwardExtensionMilestoneState):
    post_data_model = ARMAPostAwardMilestone
