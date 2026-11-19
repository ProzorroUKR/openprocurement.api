from openprocurement.tender.core.procedure.state.qualification import (
    Law4888QualificationState,
    QualificationState,
)
from openprocurement.tender.core.procedure.state.req_response import (
    ReqResponseStateMixin,
)


class QualificationReqResponseState(ReqResponseStateMixin, QualificationState):
    pass


class Law4888QualificationReqResponseState(ReqResponseStateMixin, Law4888QualificationState):
    pass
