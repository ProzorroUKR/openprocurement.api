from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.criterion_rg import (
    RequirementGroupResource as OpenUARequirementGroupResource,
)


@resource(
    name="simple.defense:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense criteria requirement group",
)
class RequirementGroupResource(OpenUARequirementGroupResource):
    pass
