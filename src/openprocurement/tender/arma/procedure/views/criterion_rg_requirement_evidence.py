from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.criterion_rg_requirement_evidence import (
    EligibleEvidenceState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)


@resource(
    name="complexAsset.arma:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender requirement evidence",
)
class EligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = EligibleEvidenceState
