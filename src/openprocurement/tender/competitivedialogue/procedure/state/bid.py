from openprocurement.tender.core.procedure.state.bid import BidState


class CDBidState(BidState):
    bid_items_quantity_required = False
    bid_value_allowed = False
    bid_parameters_allowed = False

    def validate_bid_value_on_patch(self, data):
        pass  # value is validated by the procedure's own bid model
