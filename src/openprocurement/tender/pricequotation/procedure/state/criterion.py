from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    PQTenderDetailsState,
)


class PQCriterionState(CriterionStateMixin, PQTenderDetailsState):
    pass
