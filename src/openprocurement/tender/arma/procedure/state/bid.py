from schematics.exceptions import ValidationError

from openprocurement.tender.arma.procedure.models.bid import (
    ARMABid,
    ARMAPatchBid,
    ARMAPatchQualificationBid,
    ARMAPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.utils import find_lot


class ARMABidState(BidState):
    bid_post_data_model = ARMAPostBid
    bid_patch_data_model = ARMAPatchBid
    bid_patch_qualification_data_model = ARMAPatchQualificationBid
    bid_data_model = ARMABid

    draft_bid_value_check = False
    item_patch_fields_during_qualification = {
        "requirementResponses": None,
        "subcontractingDetails": None,
        "tenderers": ("signerInfo",),
        "lotValues": ("subcontractingDetails",),
    }
    item_unit_amount_check = False
    bid_value_amount_field = "amountPercentage"

    def validate_bid_lot_value_against_lot(self, tender, lot_value):
        lot = find_lot(tender, lot_value.get("relatedLot"))
        value = lot_value["value"]
        if lot and value and lot["value"]["amountPercentage"] < value["amountPercentage"]:
            raise ValidationError("value of bid should be less than value of lot")


class ComplexAssetBidState(ARMABidState):
    pass


class SimpleAssetBidState(ARMABidState):
    pass
