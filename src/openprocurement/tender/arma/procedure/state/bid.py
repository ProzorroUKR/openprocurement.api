from openprocurement.tender.arma.procedure.models.bid import (
    ARMABid,
    ARMAPatchBid,
    ARMAPatchQualificationBid,
    ARMAPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState


class ARMABidState(BidState):
    post_data_model = ARMAPostBid
    patch_data_model = ARMAPatchBid
    patch_qualification_data_model = ARMAPatchQualificationBid
    data_model = ARMABid

    draft_bid_value_check = False
    item_patch_fields_during_qualification = {
        "requirementResponses": None,
        "subcontractingDetails": None,
        "tenderers": ("signerInfo",),
        "lotValues": ("subcontractingDetails",),
    }
    item_unit_amount_check = False
    bid_value_amount_field = "amountPercentage"
