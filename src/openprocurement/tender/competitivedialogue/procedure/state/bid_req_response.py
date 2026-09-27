from openprocurement.tender.competitivedialogue.procedure.state.bid import (
    CDBidState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CDBidReqResponseState(ReqResponseStateMixin, CDBidState):
    pass
