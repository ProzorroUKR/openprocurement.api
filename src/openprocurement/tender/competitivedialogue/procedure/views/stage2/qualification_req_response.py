from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_req_response import (
    QualificationReqResponseResource as BaseReqResponseResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@resource(
    name="{}:Qualification Requirement Response".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU qualification requirement responses",
)
class QualificationReqResponseResource(BaseReqResponseResource):
    pass
