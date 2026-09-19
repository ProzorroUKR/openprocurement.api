from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class AwardState(AwardStateMixing, RequestForProposalTenderState):
    award_cancel_claims_on_cancel = True
    sign_award_required = False
    award_unsuccessful_cancel_all_lot_awards = False  # awards after the current one only
