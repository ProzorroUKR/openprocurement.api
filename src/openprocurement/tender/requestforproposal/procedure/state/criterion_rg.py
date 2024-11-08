from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion import (
    BaseRequestForProposalCriterionStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalRequirementGroupStateMixin(
    BaseRequestForProposalCriterionStateMixin,
    RequirementGroupStateMixin,
):
    pass


class RequestForProposalRequirementGroupState(
    RequestForProposalRequirementGroupStateMixin,
    RequestForProposalTenderState,
):
    pass
