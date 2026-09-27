from openprocurement.tender.competitivedialogue.procedure.state.bid import (
    CDBidState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CDBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CDBidState):
    pass
