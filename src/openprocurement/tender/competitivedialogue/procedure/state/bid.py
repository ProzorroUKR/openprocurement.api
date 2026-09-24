from openprocurement.tender.competitivedialogue.procedure.models.bid import (
    CDBid,
    CDPatchBid,
    CDPatchQualificationBid,
    CDPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState


class CDBidState(BidState):
    post_data_model = CDPostBid
    patch_data_model = CDPatchBid
    patch_qualification_data_model = CDPatchQualificationBid
    data_model = CDBid

    bid_items_quantity_required = False
    bid_value_allowed = False
    bid_parameters_allowed = False
    bid_value_validation_on_patch = False  # value is validated by the procedure's own bid model
