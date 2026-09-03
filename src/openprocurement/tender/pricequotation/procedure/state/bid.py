from openprocurement.tender.core.procedure.state.bid import BidState


class PQBidState(BidState):
    self_eligible_required = False

    def validate_bid_value_on_patch(self, data):
        pass  # value is validated by the procedure's own bid model

    check_all_exist_tender_items = True
    items_product_required = True
