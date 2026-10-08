from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class CDStage2EURequirementGroupState(RequirementGroupStateMixin, CDStage2EUTenderDetailsState):
    pass


class CDStage2UARequirementGroupState(RequirementGroupStateMixin, CDStage2UATenderDetailsState):
    pass
