from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class BelowThresholdAwardClaimState(AwardClaimStateMixin, BelowThresholdTenderState):
    should_validate_is_satisfied = False

    def validate_submit_claim(self, claim):
        pass
