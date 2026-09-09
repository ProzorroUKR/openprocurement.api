from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class CDStage1TenderLotState(LotInvalidationBidStateMixin, CDStage1TenderDetailsStateMixin):
    lot_sets_auction_period = False
