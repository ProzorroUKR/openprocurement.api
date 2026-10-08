from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin
from openprocurement.tender.open.procedure.state.bid import (
    AboveThresholdBidState,
    AboveThresholdEUBidState,
    AboveThresholdUABidState,
    BelowThresholdBidState,
    COBidState,
    RFPBidState,
    SimpleDefenseBidState,
)


class AboveThresholdBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, AboveThresholdBidState):
    pass


class AboveThresholdUABidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, AboveThresholdUABidState):
    pass


class AboveThresholdEUBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, AboveThresholdEUBidState):
    pass


class SimpleDefenseBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, SimpleDefenseBidState):
    pass


class COBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, COBidState):
    pass


class BelowThresholdBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, BelowThresholdBidState):
    pass


class RFPBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, RFPBidState):
    pass
