from openprocurement.tender.competitivedialogue.procedure.models.award import CDAward, CDPatchAward, CDPostAward
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.state.tender import TenderState


class CDStage2AwardState(AwardStateMixing, TenderState):
    award_class = Award
    post_data_model = CDPostAward
    patch_data_model = CDPatchAward
    data_model = CDAward

    award_stand_still_working_days: bool = False
    award_has_eligible: bool = True
    award_cancel_lot_awards_on_satisfied_complaint = True
    # competitive dialogue award items do not require deliveryDate/deliveryAddress
    items_delivery_required: bool = False
    items_unit_required: bool = False
    items_quantity_required: bool = False
