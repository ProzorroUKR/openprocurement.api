from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.simpledefense.procedure.models.bid import (
    PatchBid,
    PatchQualificationBid,
)


class SimpleDefenseBidState(BidState):
    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in self.qualification_statuses:
            return PatchQualificationBid
        return PatchBid
