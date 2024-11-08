from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalAwardClaimState(AwardClaimStateMixin, RequestForProposalTenderState):
    should_validate_is_satisfied = False

    def validate_submit_claim(self, claim):
        pass
