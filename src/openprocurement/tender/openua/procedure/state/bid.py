from openprocurement.tender.core.procedure.state.bid import BidState


class OpenUABidState(BidState):
    skip_value_validation_for_draft_bid = True
