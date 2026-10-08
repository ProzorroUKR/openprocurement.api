from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin
from openprocurement.tender.esco.procedure.state.bid import (
    ESCOBidState,
)


class ESCOBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ESCOBidState):
    pass
