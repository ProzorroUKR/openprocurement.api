from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)


class PQCriterionState(CriterionStateMixin, PQTenderState):
    criterion_allowed_tender_statuses = ["draft"]
