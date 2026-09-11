from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)

# from openprocurement.tender.pricequotation.procedure.state.criterion import PQCriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)

#
#
# class PQRequirementStateMixin(PQCriterionStateMixin, RequirementStateMixin):
#     pass


class PQRequirementState(RequirementStateMixin, PriceQuotationTenderState):
    tender_valid_statuses = ["draft"]
    requirement_status_check_always = True
