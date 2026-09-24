from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.bid import BidState


class PQBidState(BidState):
    bid_create_accreditations = (AccreditationLevel.ACCR_2,)
    self_eligible_required = False

    check_all_exist_tender_items = True
    items_product_required = True
