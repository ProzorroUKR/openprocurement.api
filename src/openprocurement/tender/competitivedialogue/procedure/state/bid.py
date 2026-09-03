from openprocurement.tender.core.procedure.models.bid import CDPatchBid as PatchBid
from openprocurement.tender.core.procedure.models.bid import CDPatchQualificationBid as PatchQualificationBid
from openprocurement.tender.core.procedure.state.bid import BidState


class CDBidState(BidState):
    bid_items_quantity_required = False

    def validate_bid_value_on_patch(self, data):
        pass  # value is validated by the procedure's own bid model

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in self.qualification_statuses:
            return PatchQualificationBid
        return PatchBid
