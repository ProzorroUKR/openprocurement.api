from openprocurement.tender.competitivedialogue.procedure.state.stage2.bid import (
    CDStage2EUBidState,
    CDStage2UABidState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class CDStage2EUBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CDStage2EUBidState):
    pass


class CDStage2UABidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, CDStage2UABidState):
    pass
