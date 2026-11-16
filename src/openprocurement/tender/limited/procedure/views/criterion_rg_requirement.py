from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)
from openprocurement.tender.limited.procedure.state.criterion_rg_requirement import (
    NegotiationQuickRequirementState,
    NegotiationRequirementState,
    ReportingRequirementState,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=f"{ProcurementMethodType.REPORTING}",
    description="Tender requirement group requirement",
)
class ReportingRequirementResource(BaseRequirementResource):
    state_class = ReportingRequirementState

    def put(self):
        raise_operation_error(self.request, "Method Not Allowed", status=405)


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION}",
    description="Tender requirement group requirement",
)
class NegotiationRequirementResource(ReportingRequirementResource):
    state_class = NegotiationRequirementState


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=f"{ProcurementMethodType.NEGOTIATION_QUICK}",
    description="Tender requirement group requirement",
)
class NegotiationQuickRequirementResource(ReportingRequirementResource):
    state_class = NegotiationQuickRequirementState
