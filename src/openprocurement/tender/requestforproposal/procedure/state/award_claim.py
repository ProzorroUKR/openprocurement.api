from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPAwardClaimState(AwardClaimStateMixin, RFPTenderState):
    complaint_post_bid_owner_statuses = ("active", "unsuccessful")
    is_satisfied_check = False
    claim_submit_check = False
