from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.award_req_response_evidence import (
    AwardReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)


@resource(
    name="complexAsset.arma:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award evidences",
)
class AwardReqResponseEvidenceResource(BaseReqResponseEvidenceResource):
    pass
