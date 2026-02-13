from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.criterion_rg_requirement import (
    RequirementState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


@resource(
    name="complexAsset.arma:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = RequirementState
