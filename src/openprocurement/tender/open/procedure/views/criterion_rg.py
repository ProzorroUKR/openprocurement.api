from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.criterion_rg import (
    OpenRequirementGroupState,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_class = OpenRequirementGroupState
