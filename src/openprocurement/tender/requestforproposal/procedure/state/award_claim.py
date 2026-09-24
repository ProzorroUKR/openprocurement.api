from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalAwardClaimState(AwardClaimStateMixin, RequestForProposalTenderState):
    complaint_post_bid_owner_statuses = ("active", "unsuccessful")
    should_validate_is_satisfied = False
    claim_submit_validation = False
