from openprocurement.api.constants import WORKING_DAYS_WITH_WORKING_WEEKENDS
from openprocurement.tender.core.procedure.models.auction import DecimalAuctionLotResults, DecimalAuctionResults
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.chronograph import (
    IgnoredClaimMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS


class AboveThresholdTenderState(TenderState):
    award_class = Award


class AboveThresholdUATenderState(TenderState):
    award_class = Award


class AboveThresholdEUTenderState(TenderState):
    auction_results_model = DecimalAuctionResults
    auction_lot_results_model = DecimalAuctionLotResults
    award_class = Award


class DefenseTenderStateAwardingMixin:
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True


class DefenseTenderState(DefenseTenderStateAwardingMixin, TenderState):
    generate_award_milestones = False
    calendar = ABOVE_THRESHOLD_UA_DEFENSE_WORKING_DAYS


class SimpleDefenseTenderState(TenderState):
    calendar = WORKING_DAYS_WITH_WORKING_WEEKENDS
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True
    generate_award_milestones = False


class COTenderState(TenderState):
    award_class = Award


class BelowThresholdIgnoredClaimMixin(IgnoredClaimMixin):
    tender_claims_events = True
    tendering_end_waits_for_unanswered = False


class BelowThresholdTenderState(BelowThresholdIgnoredClaimMixin, TenderState):
    award_class = Award

    generate_award_milestones = False


class RFPIgnoredClaimMixin(IgnoredClaimMixin):
    tender_claims_events = True
    tendering_end_waits_for_unanswered = False


class RFPTenderState(RFPIgnoredClaimMixin, TenderState):
    award_class = Award

    generate_award_milestones = False
