from openprocurement.tender.core.procedure.state.bid import BidState


class PQBidState(BidState):
    check_all_exist_tender_items = True


class CataloguePQBidState(PQBidState):
    items_product_required = True
