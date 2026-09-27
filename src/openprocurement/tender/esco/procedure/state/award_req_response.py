from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin
from openprocurement.tender.esco.procedure.state.award import (
    ESCOAwardState,
)


class ESCOAwardReqResponseState(ReqResponseStateMixin, ESCOAwardState):
    pass
