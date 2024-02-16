from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.criterion_rq_requirement_evidence import (
    OpenEligibleEvidenceState,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}"
    "/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender requirement evidence",
)
class EligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = OpenEligibleEvidenceState
