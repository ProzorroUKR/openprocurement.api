from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin
from openprocurement.tender.limited.procedure.state.award import (
    NegotiationAwardState,
    NegotiationQuickAwardState,
    ReportingAwardState,
)


class ReportingAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ReportingAwardState):
    pass


class NegotiationAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, NegotiationAwardState):
    pass


class NegotiationQuickAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, NegotiationQuickAwardState):
    pass
