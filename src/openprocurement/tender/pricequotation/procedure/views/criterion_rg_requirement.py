from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)
from openprocurement.tender.pricequotation.procedure.state.criterion_rg_requirement import (
    PQRequirementState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description=f"{ProcurementMethodType.PRICE_QUOTATION} Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = PQRequirementState
