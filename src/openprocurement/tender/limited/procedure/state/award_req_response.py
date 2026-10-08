from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin
from openprocurement.tender.limited.procedure.state.award import (
    NegotiationAwardState,
    NegotiationQuickAwardState,
    ReportingAwardState,
)


class ReportingAwardReqResponseState(ReqResponseStateMixin, ReportingAwardState):
    pass


class NegotiationAwardReqResponseState(ReqResponseStateMixin, NegotiationAwardState):
    pass


class NegotiationQuickAwardReqResponseState(ReqResponseStateMixin, NegotiationQuickAwardState):
    pass
