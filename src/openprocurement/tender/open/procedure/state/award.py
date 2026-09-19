from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class AwardState(AwardStateMixing, OpenTenderState):
    award_stand_still_working_days: bool = False
    items_delivery_required: bool = True
    award_has_eligible: bool = True
    award_cancel_lot_awards_on_satisfied_complaint = True
