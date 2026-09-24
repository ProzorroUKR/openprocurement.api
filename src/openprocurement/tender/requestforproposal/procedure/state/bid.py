from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.bid import BidState


class RequestForProposalBidState(BidState):
    bid_create_accreditations = (AccreditationLevel.ACCR_2,)

    bid_patch_deleted_check = False
    items_unit_value_required_for_funders = True
    self_eligible_required = False
