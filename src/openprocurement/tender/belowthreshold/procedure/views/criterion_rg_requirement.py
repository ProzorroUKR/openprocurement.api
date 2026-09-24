from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.criterion_rg_requirement import (
    BelowThresholdRequirementState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


@resource(
    name="belowThreshold:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="belowThreshold",
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = BelowThresholdRequirementState
