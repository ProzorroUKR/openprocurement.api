from openprocurement.tender.core.procedure.models.auction import DecimalAuctionLotResults, DecimalAuctionResults
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class BaseOpenEUTenderState(TenderState):
    auction_results_model = DecimalAuctionResults
    auction_lot_results_model = DecimalAuctionLotResults
    award_class = Award

    active_bid_statuses = ("active", "pending")
