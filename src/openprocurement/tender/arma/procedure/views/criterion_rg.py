from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.criterion_rg import (
    RequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


@resource(
    name="complexAsset.arma:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_class = RequirementGroupState
