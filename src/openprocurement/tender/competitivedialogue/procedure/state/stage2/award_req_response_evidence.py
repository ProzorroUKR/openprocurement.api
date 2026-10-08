from openprocurement.tender.competitivedialogue.procedure.state.stage2.award import (
    CDStage2AwardState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CDStage2AwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CDStage2AwardState):
    pass
