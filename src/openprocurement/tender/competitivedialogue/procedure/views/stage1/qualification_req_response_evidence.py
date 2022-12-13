from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_req_response_evidence import (
    QualificationReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@resource(
    name="{}:Qualification Requirement Response Evidence".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU qualification evidences",
)
class CDEUQualificationReqResponseResource(BaseReqResponseEvidenceResource):
    pass


@resource(
    name="{}:Qualification Requirement Response Evidence".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue EU qualification evidences",
)
class CDUAQualificationReqResponseResource(BaseReqResponseEvidenceResource):
    pass
