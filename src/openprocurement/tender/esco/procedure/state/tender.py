from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.esco.procedure.models.auction import ESCOAuctionLotResults, ESCOAuctionResults
from openprocurement.tender.esco.procedure.models.award import ESCOAward


class ESCOTenderStateMixin:
    award_class = ESCOAward

    awarding_criteria_key: str = "amountPerformance"
    reverse_awarding_criteria: bool = True
    tender_weighted_value_pre_calculation: bool = False
    generate_award_milestones = False


class ESCOTenderState(ESCOTenderStateMixin, TenderState):
    auction_results_model = ESCOAuctionResults
    auction_lot_results_model = ESCOAuctionLotResults

    active_bid_statuses = ("active", "pending")
