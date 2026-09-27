from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin
from openprocurement.tender.pricequotation.procedure.state.bid import (
    PQBidState,
)


class PQBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, PQBidState):
    pass
