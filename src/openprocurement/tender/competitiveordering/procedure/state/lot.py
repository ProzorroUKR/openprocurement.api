from openprocurement.tender.competitiveordering.procedure.state.tender_details import (
    COLongTenderDetailsState,
    COShortTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class COShortTenderLotState(LotStateMixin, COShortTenderDetailsState):
    pass


class COLongTenderLotState(LotStateMixin, COLongTenderDetailsState):
    pass
