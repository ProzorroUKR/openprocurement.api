from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg import BaseRequirementGroupResource
from openprocurement.tender.esco.procedure.state.criterion_rg import ESCORequirementGroupState


@resource(
    name="esco:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="esco",
    description="Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_class = ESCORequirementGroupState
