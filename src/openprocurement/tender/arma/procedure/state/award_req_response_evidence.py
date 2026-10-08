from openprocurement.tender.arma.procedure.state.award import (
    ARMAAwardState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class ARMAAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ARMAAwardState):
    pass
