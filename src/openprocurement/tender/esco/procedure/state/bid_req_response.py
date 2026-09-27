from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin
from openprocurement.tender.esco.procedure.state.bid import (
    ESCOBidState,
)


class ESCOBidReqResponseState(ReqResponseStateMixin, ESCOBidState):
    pass
