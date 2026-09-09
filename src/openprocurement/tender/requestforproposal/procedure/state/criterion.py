from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class BaseRequestForProposalCriterionStateMixin:
    tender_valid_statuses = ["draft", "active.enquiries"]


class RequestForProposalCriterionStateMixin(BaseRequestForProposalCriterionStateMixin, CriterionStateMixin):
    criterion_patch_exclusion_check = False


class RequestForProposalCriterionState(RequestForProposalCriterionStateMixin, RequestForProposalTenderState):
    pass
