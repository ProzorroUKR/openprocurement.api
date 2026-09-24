from openprocurement.tender.esco.procedure.models.award import ESCOAward, ESCOPostAward
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as BaseAwardState,
)


class AwardState(ESCOTenderState, BaseAwardState):
    post_data_model = ESCOPostAward
    data_model = ESCOAward
    items_delivery_required: bool = False
    items_unit_required: bool = False
    items_quantity_required: bool = False
