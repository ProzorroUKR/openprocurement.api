from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.belowthreshold.procedure.state.tender_details import TenderDetailsState


class TenderLotState(LotStateMixin, TenderDetailsState):
    pass
