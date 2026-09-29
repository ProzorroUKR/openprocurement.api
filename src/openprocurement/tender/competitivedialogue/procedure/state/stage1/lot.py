from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CDStage1EUTenderLotState(LotStateMixin, CDStage1EUTenderDetailsState):
    pass


class CDStage1UATenderLotState(LotStateMixin, CDStage1UATenderDetailsState):
    pass
