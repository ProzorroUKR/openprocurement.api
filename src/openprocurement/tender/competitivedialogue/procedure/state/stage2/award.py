from openprocurement.tender.competitivedialogue.procedure.models.award import CDAward, CDPatchAward, CDPostAward
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as UAAwardState,
)


class CDStage2AwardState(UAAwardState):
    post_data_model = CDPostAward
    patch_data_model = CDPatchAward
    data_model = CDAward
    # competitive dialogue award items do not require deliveryDate/deliveryAddress
    items_delivery_required: bool = False
    items_unit_required: bool = False
    items_quantity_required: bool = False
