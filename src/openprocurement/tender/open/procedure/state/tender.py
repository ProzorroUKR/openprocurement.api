from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.utils import check_auction_period
from openprocurement.tender.open.procedure.models.award import Award


class OpenTenderState(TenderState):
    min_bids_number = 1
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    award_class = Award

    @classmethod
    def invalidate_bids_data(cls, tender):
        cls.check_auction_time(tender)
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"

    @staticmethod
    def check_auction_time(tender):
        if check_auction_period(tender.get("auctionPeriod", {}), tender):
            del tender["auctionPeriod"]["startDate"]

        for lot in tender.get("lots", ""):
            if check_auction_period(lot.get("auctionPeriod", {}), tender):
                del lot["auctionPeriod"]["startDate"]

    @staticmethod
    def check_auction_time(tender):
        if check_auction_period(tender.get("auctionPeriod", {}), tender):
            del tender["auctionPeriod"]["startDate"]

        for lot in tender.get("lots", ""):
            if check_auction_period(lot.get("auctionPeriod", {}), tender):
                del lot["auctionPeriod"]["startDate"]