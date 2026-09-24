from datetime import timedelta

from openprocurement.tender.arma.procedure.models.award import ARMAAward
from openprocurement.tender.core.procedure.models.auction import DecimalAuctionLotResults, DecimalAuctionResults
from openprocurement.tender.core.procedure.state.tender import (
    TenderState as BaseTenderState,
)


class TenderState(BaseTenderState):
    auction_results_model = DecimalAuctionResults
    auction_lot_results_model = DecimalAuctionLotResults
    award_class = ARMAAward
    active_bid_statuses = ("active", "pending")
    alp_due_date_period = timedelta(days=2)
    alp_amount_key: str = "amountPercentage"
    awarding_criteria_key: str = "amountPercentage"
    weighted_value_with_currency = False
