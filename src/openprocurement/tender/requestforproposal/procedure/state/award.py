from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class AwardState(AwardStateMixing, RequestForProposalTenderState):
    sign_award_required = False
    award_unsuccessful_cancel_forbidden_with_active_contract = True
    award_unsuccessful_cancel_requires_considered_complaints = False
