from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin
from openprocurement.tender.open.procedure.state.award import (
    AboveThresholdAwardState,
    AboveThresholdUAAwardState,
    BelowThresholdAwardState,
    COAwardState,
    RFPAwardState,
)


class AboveThresholdAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, AboveThresholdAwardState):
    pass


class AboveThresholdUAAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, AboveThresholdUAAwardState):
    pass


class COAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, COAwardState):
    pass


class BelowThresholdAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, BelowThresholdAwardState):
    pass


class RFPAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, RFPAwardState):
    pass
