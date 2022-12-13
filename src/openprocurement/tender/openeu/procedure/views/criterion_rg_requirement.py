from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement import BaseRequirementResource
from openprocurement.tender.openeu.procedure.state.criterion_rg_requirement import (
    OpenEURequirementState,
)


@resource(
    name="aboveThresholdEU:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = OpenEURequirementState
