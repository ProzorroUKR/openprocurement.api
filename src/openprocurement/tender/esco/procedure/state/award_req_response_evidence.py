from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin
from openprocurement.tender.esco.procedure.state.award import (
    ESCOAwardState,
)


class ESCOAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ESCOAwardState):
    pass
