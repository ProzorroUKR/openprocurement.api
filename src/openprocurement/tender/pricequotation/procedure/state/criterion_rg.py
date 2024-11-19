from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)

# from openprocurement.tender.pricequotation.procedure.state.criterion import PQCriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)

# class PQRequirementGroupStateMixin(PQCriterionStateMixin, RequirementGroupStateMixin):
#     pass


class PQRequirementGroupState(RequirementGroupStateMixin, PriceQuotationTenderState):
    tender_valid_statuses = ["draft"]
