from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_req_response_evidence import (
    QualificationReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@resource(
    name="{}:Qualification Requirement Response Evidence".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender EU qualification evidences",
)
class QualificationReqResponseResource(BaseReqResponseEvidenceResource):
    pass
