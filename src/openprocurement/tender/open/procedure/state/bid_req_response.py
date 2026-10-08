from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin
from openprocurement.tender.open.procedure.state.bid import (
    AboveThresholdBidState,
    AboveThresholdEUBidState,
    AboveThresholdUABidState,
    BelowThresholdBidState,
    COBidState,
    RFPBidState,
    SimpleDefenseBidState,
)


class AboveThresholdBidReqResponseState(ReqResponseStateMixin, AboveThresholdBidState):
    pass


class AboveThresholdUABidReqResponseState(ReqResponseStateMixin, AboveThresholdUABidState):
    pass


class AboveThresholdEUBidReqResponseState(ReqResponseStateMixin, AboveThresholdEUBidState):
    pass


class SimpleDefenseBidReqResponseState(ReqResponseStateMixin, SimpleDefenseBidState):
    pass


class COBidReqResponseState(ReqResponseStateMixin, COBidState):
    pass


class BelowThresholdBidReqResponseState(ReqResponseStateMixin, BelowThresholdBidState):
    pass


class RFPBidReqResponseState(ReqResponseStateMixin, RFPBidState):
    pass
