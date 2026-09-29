from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class CDStage1EURequirementState(RequirementStateMixin, CDStage1EUTenderDetailsState):
    pass


class CDStage1UARequirementState(RequirementStateMixin, CDStage1UATenderDetailsState):
    pass
