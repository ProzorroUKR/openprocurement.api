from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion import (
    BaseRequestForProposalCriterionStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalRequirementValidationsMixin:
    requirement_change_valid_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"


class RequestForProposalRequirementStateMixin(
    RequestForProposalRequirementValidationsMixin,
    BaseRequestForProposalCriterionStateMixin,
    RequirementStateMixin,
):
    pass


class RequestForProposalRequirementState(RequestForProposalRequirementStateMixin, RequestForProposalTenderState):
    allowed_put_statuses = ["active.enquiries"]
