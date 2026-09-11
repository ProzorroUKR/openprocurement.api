from openprocurement.tender.core.procedure.state.bid import BidState


class CDBidState(BidState):
    bid_items_quantity_required = False
    bid_value_allowed = False
    bid_parameters_allowed = False
    bid_value_validation_on_patch = False  # value is validated by the procedure's own bid model
