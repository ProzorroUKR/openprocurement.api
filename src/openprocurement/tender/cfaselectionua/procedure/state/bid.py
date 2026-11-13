from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.tender.cfaselectionua.procedure.models.bid import (
    CFASelectionBid,
    CFASelectionPatchBid,
    CFASelectionPatchQualificationBid,
    CFASelectionPostBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.utils import equals_decimal_and_corrupted


class CFASelectionBidState(BidState):
    post_data_model = CFASelectionPostBid
    patch_data_model = CFASelectionPatchBid
    patch_qualification_data_model = CFASelectionPatchQualificationBid
    data_model = CFASelectionBid

    def is_bid_parameter_value_allowed(self, value, feature_value):
        return equals_decimal_and_corrupted(to_decimal(value), feature_value)

    bid_create_accreditations = (AccreditationLevel.ACCR_2,)

    bid_view_forbidden_tender_statuses = ("active.tendering",)
    self_eligible_required = False
    bid_agreement_from_tender = True
    bid_agreement_check_on_patch = True
