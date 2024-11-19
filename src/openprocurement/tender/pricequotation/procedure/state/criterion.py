from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class PQCriterionState(CriterionStateMixin, PriceQuotationTenderState):
    tender_valid_statuses = ["draft"]
