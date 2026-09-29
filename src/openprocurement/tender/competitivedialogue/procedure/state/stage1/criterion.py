from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CDStage1EUCriterionState(CriterionStateMixin, CDStage1EUTenderDetailsState):
    pass


class CDStage1UACriterionState(CriterionStateMixin, CDStage1UATenderDetailsState):
    pass
