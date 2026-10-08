from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_req_response import (
    AwardReqResponseResource as BaseAwardReqResponseResource,
)
from openprocurement.tender.esco.procedure.state.award_req_response import (
    ESCOAwardReqResponseState,
)


@resource(
    name="esco:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="esco",
    description="Tender UA award requirement responses",
)
class AwardReqResponseResource(BaseAwardReqResponseResource):
    state_class = ESCOAwardReqResponseState
