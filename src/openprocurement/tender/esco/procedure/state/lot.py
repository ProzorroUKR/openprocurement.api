from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.esco.procedure.models.lot import ESCOLot, ESCOPatchLot, ESCOPostLot
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)


class ESCOTenderLotState(LotStateMixin, ESCOTenderDetailsState):
    post_data_model = ESCOPostLot
    patch_data_model = ESCOPatchLot
    data_model = ESCOLot
