from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class BidState(BaseBidState):
    self_eligible_required = False

    def validate_bid_vs_agreement(self, data):
        # cfaselectionua has agreements full copy in tender.agreements
        self.validate_bid_with_contract(data, get_tender()["agreements"][0])

    def on_patch(self, before, after):
        self.validate_bid_vs_agreement(after)
        super().on_patch(before, after)
