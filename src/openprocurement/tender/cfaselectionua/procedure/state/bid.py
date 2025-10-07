from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.cfaselectionua.procedure.models.bid import (
    PatchBid,
    PatchQualificationBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class BidState(BaseBidState):
    def validate_bid_vs_agreement(self, data):
        # cfaselectionua has agreements full copy in tender.agreements
        self.validate_bid_with_contract(data, get_tender()["agreements"][0])

    def on_patch(self, before, after):
        self.validate_bid_vs_agreement(after)
        super().on_patch(before, after)

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in self.qualification_statuses:
            return PatchQualificationBid
        return PatchBid
