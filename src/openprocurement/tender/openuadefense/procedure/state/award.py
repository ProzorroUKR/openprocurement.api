from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class AwardState(AwardStateMixing, OpenUADefenseTenderState):
    award_stand_still_working_days: bool = True
    items_delivery_required: bool = True
    award_has_eligible: bool = True
    award_new_defense_complaints_rules = True
    award_cancel_complaints_on_cancel = False
    award_cancel_satisfied_complaint_lot_awards = True
    award_unsuccessful_cancel_requires_considered_complaints = False
    award_unsuccessful_cancel_forbidden_with_active_contract = True
    award_unsuccessful_cancel_all_lot_awards = True
