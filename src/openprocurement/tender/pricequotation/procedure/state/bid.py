from openprocurement.tender.core.procedure.state.bid import BidState


class PQBidState(BidState):
    self_eligible_required = False

    check_all_exist_tender_items = True
    items_product_required = True
