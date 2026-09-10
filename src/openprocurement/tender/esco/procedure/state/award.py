from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as BaseAwardState,
)


class AwardState(ESCOTenderState, BaseAwardState):
    items_delivery_required: bool = False
    items_unit_required: bool = False
    items_quantity_required: bool = False
