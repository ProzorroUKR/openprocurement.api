from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.criterion_rg import (
    CORequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender criteria requirement group",
)
class CORequirementGroupResource(BaseRequirementGroupResource):
    state_class = CORequirementGroupState
