from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)


class RequirementGroupState(RequirementGroupStateMixin, TenderState):
    pass
