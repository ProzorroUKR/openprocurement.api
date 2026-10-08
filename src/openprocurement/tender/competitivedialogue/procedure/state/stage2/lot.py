from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CDStage2EUTenderLotState(LotStateMixin, CDStage2EUTenderDetailsState):
    pass


class CDStage2UATenderLotState(LotStateMixin, CDStage2UATenderDetailsState):
    pass
