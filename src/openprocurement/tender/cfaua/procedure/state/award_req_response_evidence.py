from openprocurement.tender.cfaua.procedure.state.award import (
    CFAUAAwardState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CFAUAAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CFAUAAwardState):
    pass
