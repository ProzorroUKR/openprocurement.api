
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderStateMixin
from openprocurement.tender.core.procedure.state.bid import BidState


class ESCOBidState(ESCOTenderStateMixin, BidState):
    pass
