from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)
from openprocurement.tender.limited.procedure.state.criterion_rg import (
    NegotiationQuickRequirementGroupState,
    NegotiationRequirementGroupState,
    ReportingRequirementGroupState,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{ProcurementMethodType.REPORTING}",
    description="Tender criteria requirement group",
)
class ReportingRequirementGroupResource(BaseRequirementGroupResource):
    state_class = ReportingRequirementGroupState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION}",
    description="Tender criteria requirement group",
)
class NegotiationRequirementGroupResource(ReportingRequirementGroupResource):
    state_class = NegotiationRequirementGroupState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION_QUICK}",
    description="Tender criteria requirement group",
)
class NegotiationQuickRequirementGroupResource(ReportingRequirementGroupResource):
    state_class = NegotiationQuickRequirementGroupState
