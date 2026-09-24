from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPCriterionStatusesMixin:
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]


class RFPCriterionStateMixin(RFPCriterionStatusesMixin, CriterionStateMixin):
    criterion_patch_exclusion_check = False


class RFPCriterionState(RFPCriterionStateMixin, RFPTenderState):
    pass
