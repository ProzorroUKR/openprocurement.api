from openprocurement.tender.core.procedure.state.bid import BidState


class CDStage2EUBidState(BidState):
    skip_value_validation_for_draft_bid = True
    bid_post_shortlisted_firms_check = True


class CDStage2UABidState(BidState):
    skip_value_validation_for_draft_bid = True
    bid_post_shortlisted_firms_check = True
