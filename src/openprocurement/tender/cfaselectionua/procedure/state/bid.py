from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.cfaselectionua.procedure.models.bid import (
    CFASelectionBid,
    CFASelectionPatchBid,
    CFASelectionPatchQualificationBid,
    CFASelectionPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState


class CFASelectionBidState(BidState):
    bid_post_data_model = CFASelectionPostBid
    bid_patch_data_model = CFASelectionPatchBid
    bid_patch_qualification_data_model = CFASelectionPatchQualificationBid
    bid_data_model = CFASelectionBid

    bid_create_accreditations = (AccreditationLevel.ACCR_2,)

    bid_view_forbidden_tender_statuses = ("active.tendering",)
    self_eligible_required = False
    bid_agreement_from_tender = True
    bid_agreement_check_on_patch = True
