from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.limited.procedure.state.criterion_rg_requirement_evidence import (
    LimitedEligibleEvidenceState,
)


@resource(
    name=f"{REPORTING}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender requirement evidence",
)
class ReportingEligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = LimitedEligibleEvidenceState


@resource(
    name=f"{NEGOTIATION}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender requirement evidence",
)
class NegotiationEligibleEvidenceResource(ReportingEligibleEvidenceResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender requirement evidence",
)
class NegotiationQuickEligibleEvidenceResource(ReportingEligibleEvidenceResource):
    pass
