from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_req_response import (
    QualificationReqResponseResource as BaseReqResponseResource,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@resource(
    name="{}:Qualification Requirement Response".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU qualification requirement responses",
)
class CDEUQualificationReqResponseResource(BaseReqResponseResource):
    pass


@resource(
    name="{}:Qualification Requirement Response".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue EU qualification requirement responses",
)
class CDUAQualificationReqResponseResource(BaseReqResponseResource):
    pass
