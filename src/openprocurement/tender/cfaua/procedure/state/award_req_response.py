from openprocurement.tender.cfaua.procedure.state.award import (
    CFAUAAwardState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CFAUAAwardReqResponseState(ReqResponseStateMixin, CFAUAAwardState):
    pass
