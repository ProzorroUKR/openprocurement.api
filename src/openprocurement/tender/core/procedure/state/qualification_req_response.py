from openprocurement.tender.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.tender.core.procedure.state.req_response import (
    ReqResponseStateMixin,
)


class QualificationReqResponseState(ReqResponseStateMixin, QualificationState):
    pass
