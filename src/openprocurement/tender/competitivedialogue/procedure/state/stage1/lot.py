from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import TenderDetailsState


class TenderLotState(LotInvalidationBidStateMixin, TenderDetailsState):

    def set_auction_period_should_start_after(self, tender: dict, data: dict) -> None:
        pass
