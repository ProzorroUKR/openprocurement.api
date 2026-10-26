from openprocurement.tender.arma.procedure.state.award import (
    ComplexAssetAwardState,
    SimpleAssetAwardState,
)
from openprocurement.tender.core.procedure.state.req_response_evidence import ReqResponseEvidenceStateMixin


class ComplexAssetAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, ComplexAssetAwardState):
    pass


class SimpleAssetAwardReqResponseEvidenceState(ReqResponseEvidenceStateMixin, SimpleAssetAwardState):
    pass
