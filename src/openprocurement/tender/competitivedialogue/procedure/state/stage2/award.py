from openprocurement.tender.openua.procedure.state.award import (
    AwardState as UAAwardState,
)


class CDStage2AwardState(UAAwardState):
    # competitive dialogue award items do not require deliveryDate/deliveryAddress
    items_delivery_required: bool = False
    items_unit_required: bool = False
    items_quantity_required: bool = False
