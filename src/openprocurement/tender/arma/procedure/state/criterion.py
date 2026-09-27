from openprocurement.tender.arma.procedure.state.tender_details import (
    ARMATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class ARMACriterionState(CriterionStateMixin, ARMATenderDetailsState):
    pass
