from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.criterion_rg import (
    CFAUARequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


@resource(
    name="closeFrameworkAgreementUA:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender criteria requirement group",
)
class RequirementGroupResource(BaseRequirementGroupResource):
    state_class = CFAUARequirementGroupState
