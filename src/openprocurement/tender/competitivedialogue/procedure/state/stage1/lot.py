from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CDStage1TenderLotState(LotStateMixin, CDStage1TenderDetailsStateMixin):
    pass
