from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import BaseEligibleEvidenceResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
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
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseEligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdEligibleEvidenceState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUAEligibleEvidenceState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUEligibleEvidenceState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUAEligibleEvidenceState, OpenTenderingEUEligibleEvidenceState
        ),
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseEligibleEvidenceState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COStateClass(
            COShortEligibleEvidenceState, COLongEligibleEvidenceState
        ),
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdEligibleEvidenceState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPEligibleEvidenceState,
    }
