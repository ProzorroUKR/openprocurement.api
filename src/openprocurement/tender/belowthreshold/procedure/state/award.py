from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.award import AwardStateMixing


class AwardState(AwardStateMixing, BelowThresholdTenderState):
    award_unsuccessful_cancel_requires_considered_complaints = False
    award_unsuccessful_cancel_forbidden_with_active_contract = True
    award_unsuccessful_cancel_all_lot_awards = True
