from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_req_response import (
    QualificationReqResponseResource as BaseReqResponseResource,
)


@resource(
    name="belowThreshold:Qualification Requirement Response",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="belowThreshold",
    description="belowThreshold qualification requirement responses",
)
class QualificationReqResponseResource(BaseReqResponseResource):
    pass
