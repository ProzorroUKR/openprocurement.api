from openprocurement.tender.competitivedialogue.procedure.models.bid import (
    CDBid,
    CDPatchBid,
    CDPatchQualificationBid,
    CDPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState


class CDBidState(BidState):
    bid_post_data_model = CDPostBid
    bid_patch_data_model = CDPatchBid
    bid_patch_qualification_data_model = CDPatchQualificationBid
    bid_data_model = CDBid

    bid_items_quantity_required = False
    bid_value_allowed = False
    bid_parameters_allowed = False
