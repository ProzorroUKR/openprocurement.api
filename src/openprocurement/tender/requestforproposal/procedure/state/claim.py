from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalTenderClaimState(ClaimStateMixin, RequestForProposalTenderState):
    update_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
    patch_as_complaint_owner_tender_statuses = (
        "active.enquiries",
        "active.tendering",
    )
    should_validate_is_satisfied = False

    def validate_submit_claim(self, claim):
        pass
