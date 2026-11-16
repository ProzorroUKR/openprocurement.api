from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_req_response_evidence import AwardReqResponseEvidenceResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.award_req_response_evidence import (
    AboveThresholdAwardReqResponseEvidenceState,
    AboveThresholdUAAwardReqResponseEvidenceState,
    BelowThresholdAwardReqResponseEvidenceState,
    COAwardReqResponseEvidenceState,
    OpenTenderingAwardReqResponseEvidenceState,
    RFPAwardReqResponseEvidenceState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    description="Tender award evidences",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenAwardReqResponseEvidenceResource(AwardReqResponseEvidenceResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdAwardReqResponseEvidenceState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUAAwardReqResponseEvidenceState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdUAAwardReqResponseEvidenceState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingAwardReqResponseEvidenceState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COAwardReqResponseEvidenceState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdAwardReqResponseEvidenceState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPAwardReqResponseEvidenceState,
    }
