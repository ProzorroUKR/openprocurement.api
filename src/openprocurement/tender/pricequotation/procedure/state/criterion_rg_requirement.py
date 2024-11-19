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

    def requirement_always(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        super().requirement_always(data)
