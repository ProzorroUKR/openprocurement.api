from openprocurement.tender.cfaselectionua.procedure.state.award import (
    CFASelectionAwardState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CFASelectionAwardReqResponseState(ReqResponseStateMixin, CFASelectionAwardState):
    pass
