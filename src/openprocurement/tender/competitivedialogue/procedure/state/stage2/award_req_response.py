from openprocurement.tender.competitivedialogue.procedure.state.stage2.award import (
    CDStage2AwardState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class CDStage2AwardReqResponseState(ReqResponseStateMixin, CDStage2AwardState):
    pass
