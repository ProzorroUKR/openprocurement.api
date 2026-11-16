from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
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
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender award requirement responses",
)
class AwardReqResponseResource(BaseAwardReqResponseResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetAwardReqResponseState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetAwardReqResponseState,
    }
