from openprocurement.tender.arma.procedure.models.bid import (
    PatchBid,
    PatchQualificationBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class BidState(BaseBidState):
    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in self.qualification_statuses:
            return PatchQualificationBid
        return PatchBid
