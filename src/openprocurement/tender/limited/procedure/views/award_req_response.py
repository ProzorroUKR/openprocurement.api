from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_req_response import (
    AwardReqResponseResource as BaseAwardReqResponseResource,
)
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING


@resource(
    name=f"{REPORTING}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender award requirement responses",
)
class ReportingAwardReqResponseResource(BaseAwardReqResponseResource):
    pass


@resource(
    name=f"{NEGOTIATION}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender award requirement responses",
)
class NegotiationAwardReqResponseResource(BaseAwardReqResponseResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender award requirement responses",
)
class NegotiationQuickAwardReqResponseResource(BaseAwardReqResponseResource):
    pass
