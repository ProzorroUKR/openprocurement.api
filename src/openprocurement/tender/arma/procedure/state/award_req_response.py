from openprocurement.tender.arma.procedure.state.award import (
    ARMAAwardState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class ARMAAwardReqResponseState(ReqResponseStateMixin, ARMAAwardState):
    pass
