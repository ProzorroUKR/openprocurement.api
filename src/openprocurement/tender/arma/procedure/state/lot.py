from openprocurement.tender.arma.procedure.models.lot import ARMALot, ARMAPatchLot, ARMAPostLot
from openprocurement.tender.arma.procedure.state.tender_details import (
    ARMATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class ARMALotState(LotStateMixin, ARMATenderDetailsState):
    post_data_model = ARMAPostLot
    patch_data_model = ARMAPatchLot
    data_model = ARMALot
