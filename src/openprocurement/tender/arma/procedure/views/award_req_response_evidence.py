from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.award_req_response_evidence import (
    ComplexAssetAwardReqResponseEvidenceState,
    SimpleAssetAwardReqResponseEvidenceState,
)
from openprocurement.tender.core.procedure.views.award_req_response_evidence import (
    AwardReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender award evidences",
)
class AwardReqResponseEvidenceResource(BaseReqResponseEvidenceResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetAwardReqResponseEvidenceState,
        SIMPLE_ASSET_ARMA: SimpleAssetAwardReqResponseEvidenceState,
    }
