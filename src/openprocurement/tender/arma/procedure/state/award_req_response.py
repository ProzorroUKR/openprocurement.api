from openprocurement.tender.arma.procedure.state.award import (
    ComplexAssetAwardState,
    SimpleAssetAwardState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class ComplexAssetAwardReqResponseState(ReqResponseStateMixin, ComplexAssetAwardState):
    pass


class SimpleAssetAwardReqResponseState(ReqResponseStateMixin, SimpleAssetAwardState):
    pass
