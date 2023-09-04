from openprocurement.tender.core.procedure.state.award_claim import AwardClaimState


class BelowThresholdAwardClaimState(AwardClaimState):
    def validate_submit_claim(self, claim):
        pass

    def validate_satisfied(self, satisfied):
        return isinstance(satisfied, bool)
