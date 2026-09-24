from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPAwardState(AwardStateMixin, RFPTenderState):
    award_cancel_claims_on_cancel = True
    sign_award_required = False
    award_unsuccessful_cancel_all_lot_awards = False  # awards after the current one only
    award_cancel_lot_awards_on_satisfied_complaint = False
    award_has_eligible = False
    award_stand_still_working_days = True
