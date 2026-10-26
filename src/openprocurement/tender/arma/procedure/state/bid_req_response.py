from openprocurement.tender.arma.procedure.state.bid import (
    ComplexAssetBidState,
    SimpleAssetBidState,
)
from openprocurement.tender.core.procedure.state.req_response import ReqResponseStateMixin


class ComplexAssetBidReqResponseState(ReqResponseStateMixin, ComplexAssetBidState):
    pass


class SimpleAssetBidReqResponseState(ReqResponseStateMixin, SimpleAssetBidState):
    pass
