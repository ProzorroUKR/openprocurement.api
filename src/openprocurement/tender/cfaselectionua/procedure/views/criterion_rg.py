from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.criterion_rg import (
    CFASelectionRequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_class = CFASelectionRequirementGroupState
