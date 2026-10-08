from openprocurement.tender.competitivedialogue.procedure.state.stage2.bid import (
    CDStage2EUBidState,
    CDStage2UABidState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CDStage2EUBidReqResponseState(ReqResponseStateMixin, CDStage2EUBidState):
    pass


class CDStage2UABidReqResponseState(ReqResponseStateMixin, CDStage2UABidState):
    pass
