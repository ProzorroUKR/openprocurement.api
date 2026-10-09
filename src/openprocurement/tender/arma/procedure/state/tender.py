from datetime import timedelta

from openprocurement.tender.arma.procedure.models.award import ARMAAward
from openprocurement.tender.core.constants import ARMA_ALP_MILESTONE_REASONS
from openprocurement.tender.core.procedure.context import get_bids_before_auction_results_context
from openprocurement.tender.core.procedure.models.auction import DecimalAuctionLotResults, DecimalAuctionResults
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import activate_bids


class ARMATenderState(TenderState):
    auction_results_model = DecimalAuctionResults
    auction_lot_results_model = DecimalAuctionLotResults
    award_class = ARMAAward

    alp_due_date_period = timedelta(days=2)
    alp_amount_key: str = "amountPercentage"
    alp_milestone_reasons: tuple = ARMA_ALP_MILESTONE_REASONS
    awarding_criteria_key: str = "amountPercentage"
    weighted_value_with_currency = False

    def get_mean_value_tendering_bids(self, tender, bids, exclude_bid_id, lot_id=None):
        # ARMA (complexAsset.arma / simpleAsset.arma) keeps the pre-auction ALP calculation:
        # mean is based on initial tendering prices.
        before_auction_bids = get_bids_before_auction_results_context()
        before_auction_bids = activate_bids(before_auction_bids)
        before_auction_bids = self.prepare_bids_for_awarding(
            tender,
            before_auction_bids,
            lot_id=lot_id,
        )
        initial_amounts = {b["id"]: float(b["value"][self.alp_amount_key]) for b in before_auction_bids}
        initial_values = [initial_amounts[b["id"]] for b in bids if b["id"] != exclude_bid_id]
        mean_value = sum(initial_values) / float(len(initial_values))
        return mean_value
