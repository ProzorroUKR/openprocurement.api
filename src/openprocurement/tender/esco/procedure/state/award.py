from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.esco.procedure.models.award import ESCOAward, ESCOPostAward
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class AwardState(AwardStateMixing, ESCOTenderState):
    post_data_model = ESCOPostAward
    data_model = ESCOAward

    award_stand_still_working_days: bool = False
    award_has_eligible: bool = True
    award_cancel_lot_awards_on_satisfied_complaint = True
    items_delivery_required: bool = False
    items_unit_required: bool = False
    items_quantity_required: bool = False
