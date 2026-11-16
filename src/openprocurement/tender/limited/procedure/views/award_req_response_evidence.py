from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_req_response_evidence import (
    AwardReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)
from openprocurement.tender.limited.procedure.state.award_req_response_evidence import (
    NegotiationAwardReqResponseEvidenceState,
    NegotiationQuickAwardReqResponseEvidenceState,
    ReportingAwardReqResponseEvidenceState,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=f"{ProcurementMethodType.REPORTING}",
    description="Tender award evidences",
)
class ReportingAwardReqResponseResource(BaseReqResponseEvidenceResource):
    state_class = ReportingAwardReqResponseEvidenceState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION}",
    description="Tender award evidences",
)
class NegotiationAwardReqResponseResource(BaseReqResponseEvidenceResource):
    state_class = NegotiationAwardReqResponseEvidenceState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION_QUICK}",
    description="Tender award evidences",
)
class NegotiationQuickAwardReqResponseResource(BaseReqResponseEvidenceResource):
    state_class = NegotiationQuickAwardReqResponseEvidenceState
