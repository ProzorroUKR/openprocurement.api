from openprocurement.tender.cfaselectionua.procedure.state.bid import (
    CFASelectionBidState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CFASelectionBidReqResponseState(ReqResponseStateMixin, CFASelectionBidState):
    pass
