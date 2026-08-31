from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_req_response_evidence import (
    AwardReqResponseEvidenceResource as BaseReqResponseEvidenceResource,
)
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING


@resource(
    name=f"{REPORTING}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender award evidences",
)
class ReportingAwardReqResponseResource(BaseReqResponseEvidenceResource):
    pass


@resource(
    name=f"{NEGOTIATION}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender award evidences",
)
class NegotiationAwardReqResponseResource(BaseReqResponseEvidenceResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender award evidences",
)
class NegotiationQuickAwardReqResponseResource(BaseReqResponseEvidenceResource):
    pass
