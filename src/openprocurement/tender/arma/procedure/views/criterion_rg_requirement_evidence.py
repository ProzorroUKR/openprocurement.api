from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.criterion_rg_requirement_evidence import (
    ComplexAssetEligibleEvidenceState,
    SimpleAssetEligibleEvidenceState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender requirement evidence",
)
class EligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetEligibleEvidenceState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetEligibleEvidenceState,
    }
