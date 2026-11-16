from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.criterion_rg_requirement import (
    ComplexAssetRequirementState,
    SimpleAssetRequirementState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetRequirementState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetRequirementState,
    }
