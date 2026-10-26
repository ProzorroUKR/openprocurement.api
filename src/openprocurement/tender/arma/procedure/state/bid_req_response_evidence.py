from openprocurement.tender.arma.procedure.state.bid import (
    ComplexAssetBidState,
    SimpleAssetBidState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class ComplexAssetBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ComplexAssetBidState):
    pass


class SimpleAssetBidReqResponseEvidenceState(ReqResponseEvidenceStateMixin, SimpleAssetBidState):
    pass
