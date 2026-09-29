from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class CDStage1EURequirementGroupState(RequirementGroupStateMixin, CDStage1EUTenderDetailsState):
    pass


class CDStage1UARequirementGroupState(RequirementGroupStateMixin, CDStage1UATenderDetailsState):
    pass
