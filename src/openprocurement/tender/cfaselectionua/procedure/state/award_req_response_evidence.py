from openprocurement.tender.cfaselectionua.procedure.state.award import (
    CFASelectionAwardState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CFASelectionAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CFASelectionAwardState):
    pass
