from openprocurement.tender.cfaselectionua.procedure.state.bid import (
    CFASelectionBidState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CFASelectionBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CFASelectionBidState):
    pass
