from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.award import AwardStateMixing


class COAwardState(AwardStateMixing, COTenderState):
    award_stand_still_working_days: bool = False
    items_delivery_required: bool = True
    award_has_eligible: bool = True
    award_eligible_rules_by_creation_date = True
    award_cancel_complaints_on_cancel = False
    award_cancel_satisfied_complaint_lot_awards = True
