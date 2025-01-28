from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class CDStage1TenderLotState(LotInvalidationBidStateMixin, CDStage1TenderDetailsStateMixin):
    def set_auction_period_should_start_after(self, tender: dict, data: dict) -> None:
        pass
