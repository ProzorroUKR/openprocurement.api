from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)


class CDRequirementGroupState(RequirementGroupStateMixin, CDStage1TenderState):
    pass
