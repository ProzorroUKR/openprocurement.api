from openprocurement.tender.core.procedure.state.bid import BidState


class RequestForProposalBidState(BidState):
    items_unit_value_required_for_funders = True
