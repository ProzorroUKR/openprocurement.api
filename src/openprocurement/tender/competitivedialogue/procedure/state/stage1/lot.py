from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import Stage1TenderState
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import TenderDetailsState


class TenderLotState(LotInvalidationBidStateMixin, Stage1TenderState):
    tender_details_state_class = TenderDetailsState

    def set_auction_period_should_start_after(self, tender: dict, data: dict) -> None:
        pass
