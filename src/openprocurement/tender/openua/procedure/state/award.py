from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class AwardState(AwardStateMixing, OpenUATenderState):
    award_stand_still_working_days: bool = False
    items_delivery_required: bool = True
    award_has_eligible: bool = True
    award_cancel_complaints_on_cancel = False
    award_cancel_satisfied_complaint_lot_awards = True
    award_unsuccessful_cancel_requires_considered_complaints = False
    award_unsuccessful_cancel_forbidden_with_active_contract = True
    award_unsuccessful_cancel_all_lot_awards = True
