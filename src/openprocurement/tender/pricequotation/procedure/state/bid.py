from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class BidState(BaseBidState):
    def validate_bid_vs_agreement(self, data):
        # skip main agreement validation logic
        pass
