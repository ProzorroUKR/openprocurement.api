from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.state.criterion_rg import (
    PQRequirementGroupState,
)


@resource(
    name=f"{PQ}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{PQ}",
    description=f"{PQ} Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_class = PQRequirementGroupState
