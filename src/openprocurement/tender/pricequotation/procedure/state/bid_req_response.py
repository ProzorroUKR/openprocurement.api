from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin
from openprocurement.tender.pricequotation.procedure.state.bid import (
    PQBidState,
)


class PQBidReqResponseState(ReqResponseStateMixin, PQBidState):
    pass
