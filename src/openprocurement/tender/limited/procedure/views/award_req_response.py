from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_req_response import (
    AwardReqResponseResource as BaseAwardReqResponseResource,
)
from openprocurement.tender.limited.procedure.state.award_req_response import (
    NegotiationAwardReqResponseState,
    NegotiationQuickAwardReqResponseState,
    ReportingAwardReqResponseState,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=f"{ProcurementMethodType.REPORTING}",
    description="Tender award requirement responses",
)
class ReportingAwardReqResponseResource(BaseAwardReqResponseResource):
    state_class = ReportingAwardReqResponseState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION}",
    description="Tender award requirement responses",
)
class NegotiationAwardReqResponseResource(BaseAwardReqResponseResource):
    state_class = NegotiationAwardReqResponseState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION_QUICK}",
    description="Tender award requirement responses",
)
class NegotiationQuickAwardReqResponseResource(BaseAwardReqResponseResource):
    state_class = NegotiationQuickAwardReqResponseState
