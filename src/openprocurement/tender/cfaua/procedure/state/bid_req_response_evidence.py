from openprocurement.tender.cfaua.procedure.state.bid import (
    CFAUABidState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CFAUABidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CFAUABidState):
    pass
