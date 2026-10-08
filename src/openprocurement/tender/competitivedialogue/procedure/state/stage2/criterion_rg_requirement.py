from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class CDStage2EURequirementState(RequirementStateMixin, CDStage2EUTenderDetailsState):
    pass


class CDStage2UARequirementState(RequirementStateMixin, CDStage2UATenderDetailsState):
    pass
