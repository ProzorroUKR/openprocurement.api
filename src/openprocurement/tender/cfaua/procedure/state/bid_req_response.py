from openprocurement.tender.cfaua.procedure.state.bid import (
    CFAUABidState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CFAUABidReqResponseState(ReqResponseStateMixin, CFAUABidState):
    pass
