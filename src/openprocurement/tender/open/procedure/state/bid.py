from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.bid import BidState


class AboveThresholdBidState(BidState):
    draft_bid_value_check = False


class AboveThresholdUABidState(BidState):
    draft_bid_value_check = False


class AboveThresholdEUBidState(BidState):
    draft_bid_value_check = False


class DefenseBidState(BidState):
    self_eligible_rogue_after_ecriteria = False
    requirement_responses_allowed = False


class SimpleDefenseBidState(BidState):
    self_eligible_rogue_after_ecriteria = False


class COBidState(BidState):
    draft_bid_value_check = False


class BelowThresholdBidState(BidState):
    bid_create_accreditations = (AccreditationLevel.ACCR_2,)

    bid_patch_deleted_check = False
    items_unit_value_required_for_funders = True
    self_eligible_required = False


class RFPBidState(BidState):
    bid_create_accreditations = (AccreditationLevel.ACCR_2,)

    bid_patch_deleted_check = False
    items_unit_value_required_for_funders = True
    self_eligible_required = False
