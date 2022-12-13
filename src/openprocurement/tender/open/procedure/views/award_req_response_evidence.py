from cornice.resource import resource

from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.core.procedure.views.award_req_response_evidence import (
    AwardReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)


@resource(
    name=f"{ABOVE_THRESHOLD}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender award evidences",
)
class AwardReqResponseResource(BaseReqResponseEvidenceResource):
    pass
