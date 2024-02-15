from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.criterion_rg_requirement import (
    OpenRequirementState,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = OpenRequirementState
