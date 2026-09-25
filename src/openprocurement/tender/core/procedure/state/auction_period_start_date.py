from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.models.auction import AuctionPeriodStartDate
from openprocurement.tender.core.procedure.state.tender import TenderState


class AuctionPeriodStartDateState(TenderState):
    put_data_model = AuctionPeriodStartDate

    def validate_auction_period_put_request(self):
        tender = get_tender()
        if tender["status"] not in ("active.auction", "active.pre-qualification", "active.tendering"):
            raise_operation_error(
                self.request, f"Can't update auctionPeriod in current ({tender['status']}) tender status"
            )
        lot_id = self.request.matchdict.get("lot_id")
        if lot_id and not any(lot["status"] == "active" for lot in tender.get("lots", "") if lot["id"] == lot_id):
            raise_operation_error(self.request, "Can update auction urls only in active lot status")
        self.validate_input_data(self.put_data_model)
