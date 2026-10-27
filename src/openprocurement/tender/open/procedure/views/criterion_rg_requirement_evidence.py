from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import BaseEligibleEvidenceResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    OPEN_TENDERING,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.criterion_rg_requirement_evidence import (
    AboveThresholdEligibleEvidenceState,
    AboveThresholdEUEligibleEvidenceState,
    AboveThresholdUAEligibleEvidenceState,
    BelowThresholdEligibleEvidenceState,
    COLongEligibleEvidenceState,
    COShortEligibleEvidenceState,
    OpenTenderingEUEligibleEvidenceState,
    OpenTenderingUAEligibleEvidenceState,
    RFPEligibleEvidenceState,
    SimpleDefenseEligibleEvidenceState,
)
from openprocurement.tender.open.procedure.views.base import (
    COStateClass,
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    description="Tender requirement evidence",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        OPEN_TENDERING,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseEligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdEligibleEvidenceState,
        ABOVE_THRESHOLD_UA: AboveThresholdUAEligibleEvidenceState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUEligibleEvidenceState,
        OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUAEligibleEvidenceState, OpenTenderingEUEligibleEvidenceState
        ),
        SIMPLE_DEFENSE: SimpleDefenseEligibleEvidenceState,
        COMPETITIVE_ORDERING: COStateClass(COShortEligibleEvidenceState, COLongEligibleEvidenceState),
        BELOW_THRESHOLD: BelowThresholdEligibleEvidenceState,
        REQUEST_FOR_PROPOSAL: RFPEligibleEvidenceState,
    }
