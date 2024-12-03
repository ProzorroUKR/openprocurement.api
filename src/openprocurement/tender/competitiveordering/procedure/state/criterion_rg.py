from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)


class OpenRequirementGroupState(RequirementGroupStateMixin, OpenTenderState):
    pass
