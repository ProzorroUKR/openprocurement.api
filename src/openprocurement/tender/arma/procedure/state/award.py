from openprocurement.tender.arma.procedure.models.award import ARMAAward, ARMAPostAward
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.award import AwardStateMixing


class AwardState(AwardStateMixing, TenderState):
    post_data_model = ARMAPostAward
    data_model = ARMAAward
    award_class = ARMAAward

    award_stand_still_working_days: bool = False
    items_delivery_required: bool = True
    award_has_eligible: bool = True
    award_cancel_lot_awards_on_satisfied_complaint = True
