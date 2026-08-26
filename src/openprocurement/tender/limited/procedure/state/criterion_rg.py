from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState


class LimitedRequirementGroupState(
    RequirementGroupStateMixin,
    TenderState,
):
    pass
