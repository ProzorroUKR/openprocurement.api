from openprocurement.tender.arma.procedure.models.lot import ARMALot, ARMAPatchLot, ARMAPostLot
from openprocurement.tender.arma.procedure.state.tender_details import (
    ComplexAssetTenderDetailsState,
    SimpleAssetTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class ARMALotStateMixin(LotStateMixin):
    post_data_model = ARMAPostLot
    patch_data_model = ARMAPatchLot
    data_model = ARMALot


class ComplexAssetLotState(ARMALotStateMixin, ComplexAssetTenderDetailsState):
    pass


class SimpleAssetLotState(ARMALotStateMixin, SimpleAssetTenderDetailsState):
    pass
