from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_req_response_evidence import (
    AwardReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender award evidences",
)
class AwardReqResponseResource(BaseReqResponseEvidenceResource):
    pass
