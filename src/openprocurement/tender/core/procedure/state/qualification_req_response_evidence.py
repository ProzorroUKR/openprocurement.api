from openprocurement.tender.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import (
    ReqResponseEvidenceStateMixin,
)


class QualificationReqResponseEvidenceState(ReqResponseEvidenceStateMixin, QualificationState):
    pass
