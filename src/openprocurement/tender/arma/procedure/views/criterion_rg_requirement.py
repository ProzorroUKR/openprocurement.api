from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
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
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetRequirementState,
        SIMPLE_ASSET_ARMA: SimpleAssetRequirementState,
    }
