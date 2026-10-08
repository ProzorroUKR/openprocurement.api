from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CDStage2EUCriterionState(CriterionStateMixin, CDStage2EUTenderDetailsState):
    pass


class CDStage2UACriterionState(CriterionStateMixin, CDStage2UATenderDetailsState):
    pass
