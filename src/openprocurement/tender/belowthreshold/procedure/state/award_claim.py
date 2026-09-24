from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class BelowThresholdAwardClaimState(AwardClaimStateMixin, BelowThresholdTenderState):
    complaint_post_bid_owner_statuses = ("active", "unsuccessful")
    is_satisfied_check = False
    claim_submit_check = False
