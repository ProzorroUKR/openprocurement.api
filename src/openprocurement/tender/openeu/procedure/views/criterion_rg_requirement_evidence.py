from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)
from openprocurement.tender.openeu.procedure.state.criterion_rg_requirement_evidence import (
    OpenEUEligibleEvidenceState,
)


@resource(
    name="aboveThresholdEU:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender requirement evidence",
)
class EligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = OpenEUEligibleEvidenceState
