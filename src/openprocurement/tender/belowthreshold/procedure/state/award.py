from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.award import AwardStateMixin


class BelowThresholdAwardState(AwardStateMixin, BelowThresholdTenderState):
    award_cancel_claims_on_cancel = True
    award_cancel_lot_awards_on_satisfied_complaint = False
    award_has_eligible = False
    award_stand_still_working_days = True
