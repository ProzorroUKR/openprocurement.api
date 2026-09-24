from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    RFPTenderState,
)


class AboveThresholdCriterionState(CriterionStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUACriterionState(CriterionStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEUCriterionState(CriterionStateMixin, AboveThresholdEUTenderState):
    pass


class COCriterionState(CriterionStateMixin, COTenderState):
    pass


class BelowThresholdCriterionStatusesMixin:
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]


class BelowThresholdCriterionStateMixin(BelowThresholdCriterionStatusesMixin, CriterionStateMixin):
    criterion_patch_exclusion_check = False


class BelowThresholdCriterionState(BelowThresholdCriterionStateMixin, BelowThresholdTenderState):
    pass


class RFPCriterionStatusesMixin:
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]


class RFPCriterionStateMixin(RFPCriterionStatusesMixin, CriterionStateMixin):
    criterion_patch_exclusion_check = False


class RFPCriterionState(RFPCriterionStateMixin, RFPTenderState):
    pass
