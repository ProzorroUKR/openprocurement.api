from openprocurement.tender.core.procedure.state.bid import BidState


class CDStage2EUBidState(BidState):
    draft_bid_value_check = False
    bid_post_shortlisted_firms_check = True


class CDStage2UABidState(BidState):
    draft_bid_value_check = False
    bid_post_shortlisted_firms_check = True
