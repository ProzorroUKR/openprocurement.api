from openprocurement.tender.core.procedure.state.bid import BidState


class OpenEUBidState(BidState):
    skip_value_validation_for_draft_bid = True
