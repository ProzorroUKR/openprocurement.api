from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)


class ESCOCriterionState(CriterionStateMixin, ESCOTenderDetailsState):
    pass
