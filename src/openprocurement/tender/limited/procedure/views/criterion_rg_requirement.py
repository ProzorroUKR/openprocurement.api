from cornice.resource import resource

from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.limited.procedure.state.criterion_rg_requirement import LimitedRequirementState


@resource(
    name=f"{REPORTING}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender requirement group requirement",
)
class ReportingRequirementResource(BaseRequirementResource):
    state_class = LimitedRequirementState

    def put(self):
        raise_operation_error(self.request, "Method Not Allowed", status=405)


@resource(
    name=f"{NEGOTIATION}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender requirement group requirement",
)
class NegotiationRequirementResource(ReportingRequirementResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender requirement group requirement",
)
class NegotiationQuickRequirementResource(ReportingRequirementResource):
    pass
