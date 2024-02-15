from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class BelowThresholdAwardClaimState(AwardClaimStateMixin, BelowThresholdTenderState):
    def validate_submit_claim(self, claim):
        pass

    def validate_satisfied(self, satisfied):
        return isinstance(satisfied, bool)
