from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.criterion_rg_requirement import (
    RequirementResource as OpenUARequirementResource,
)


@resource(
    name="simple.defense:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense requirement group requirement",
)
class RequirementResource(OpenUARequirementResource):
    pass
