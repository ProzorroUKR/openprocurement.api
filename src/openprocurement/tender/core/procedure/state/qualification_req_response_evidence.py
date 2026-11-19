from openprocurement.tender.core.procedure.state.qualification import (
    Law4888QualificationState,
    QualificationState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import (
    ReqResponseEvidenceStateMixin,
)


class QualificationReqResponseEvidenceState(ReqResponseEvidenceStateMixin, QualificationState):
    pass


class Law4888QualificationReqResponseEvidenceState(ReqResponseEvidenceStateMixin, Law4888QualificationState):
    pass
