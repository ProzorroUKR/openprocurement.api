from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion import (
    RFPCriterionStatusesMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPRequirementGroupStateMixin(
    RFPCriterionStatusesMixin,
    RequirementGroupStateMixin,
):
    pass


class RFPRequirementGroupState(
    RFPRequirementGroupStateMixin,
    RFPTenderState,
):
    pass
