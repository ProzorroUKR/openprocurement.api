from openprocurement.tender.core.procedure.state.bid import BidState


class PQBidState(BidState):
    check_all_exist_tender_items = True
