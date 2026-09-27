from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin
from openprocurement.tender.open.procedure.state.award import (
    AboveThresholdAwardState,
    AboveThresholdUAAwardState,
    BelowThresholdAwardState,
    COAwardState,
    RFPAwardState,
)


class AboveThresholdAwardReqResponseState(ReqResponseStateMixin, AboveThresholdAwardState):
    pass


class AboveThresholdUAAwardReqResponseState(ReqResponseStateMixin, AboveThresholdUAAwardState):
    pass


class COAwardReqResponseState(ReqResponseStateMixin, COAwardState):
    pass


class BelowThresholdAwardReqResponseState(ReqResponseStateMixin, BelowThresholdAwardState):
    pass


class RFPAwardReqResponseState(ReqResponseStateMixin, RFPAwardState):
    pass
