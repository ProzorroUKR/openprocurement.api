from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.award_req_response import (
    ComplexAssetAwardReqResponseState,
    SimpleAssetAwardReqResponseState,
)
from openprocurement.tender.core.procedure.views.award_req_response import (
    AwardReqResponseResource as BaseAwardReqResponseResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender award requirement responses",
)
class AwardReqResponseResource(BaseAwardReqResponseResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetAwardReqResponseState,
        SIMPLE_ASSET_ARMA: SimpleAssetAwardReqResponseState,
    }
