from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.limited.procedure.state.criterion_rg import LimitedRequirementGroupState


@resource(
    name=f"{REPORTING}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender criteria requirement group",
)
class ReportingRequirementGroupResource(BaseRequirementGroupResource):
    state_class = LimitedRequirementGroupState


@resource(
    name=f"{NEGOTIATION}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender criteria requirement group",
)
class NegotiationRequirementGroupResource(ReportingRequirementGroupResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender criteria requirement group",
)
class NegotiationQuickRequirementGroupResource(ReportingRequirementGroupResource):
    pass
