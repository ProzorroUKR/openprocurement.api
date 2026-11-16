from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)
from openprocurement.tender.limited.procedure.state.criterion_rg_requirement_evidence import (
    NegotiationEligibleEvidenceState,
    NegotiationQuickEligibleEvidenceState,
    ReportingEligibleEvidenceState,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=f"{ProcurementMethodType.REPORTING}",
    description="Tender requirement evidence",
)
class ReportingEligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = ReportingEligibleEvidenceState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION}",
    description="Tender requirement evidence",
)
class NegotiationEligibleEvidenceResource(ReportingEligibleEvidenceResource):
    state_class = NegotiationEligibleEvidenceState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION_QUICK}",
    description="Tender requirement evidence",
)
class NegotiationQuickEligibleEvidenceResource(ReportingEligibleEvidenceResource):
    state_class = NegotiationQuickEligibleEvidenceState
