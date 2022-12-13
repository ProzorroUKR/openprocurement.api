from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.criterion_rg_requirement import (
    CFASelectionRequirementState,
)
from openprocurement.tender.belowthreshold.procedure.views.criterion_rg_requirement import (
    RequirementResource as BaseRequirementResource
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = CFASelectionRequirementState
