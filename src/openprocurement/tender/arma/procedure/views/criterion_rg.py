from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.criterion_rg import (
    ComplexAssetRequirementGroupState,
    SimpleAssetRequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetRequirementGroupState,
        SIMPLE_ASSET_ARMA: SimpleAssetRequirementGroupState,
    }
