from openprocurement.tender.arma.procedure.models.bid import (
    ARMABid,
    ARMAPatchBid,
    ARMAPatchQualificationBid,
    ARMAPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class BidState(BaseBidState):
    post_data_model = ARMAPostBid
    patch_data_model = ARMAPatchBid
    patch_qualification_data_model = ARMAPatchQualificationBid
    data_model = ARMABid
    skip_value_validation_for_draft_bid = True
    item_patch_fields_during_qualification = {
        "requirementResponses": None,
        "subcontractingDetails": None,
        "tenderers": ("signerInfo",),
        "lotValues": ("subcontractingDetails",),
    }
    check_item_unit_amount = False
    bid_value_amount_field = "amountPercentage"
