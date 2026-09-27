from openprocurement.tender.arma.procedure.state.bid import (
    ARMABidState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class ARMABidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ARMABidState):
    pass
