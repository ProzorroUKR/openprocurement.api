from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class BelowThresholdCriterionStatusesMixin:
    criterion_allowed_tender_statuses = ["draft", "active.enquiries"]


class BelowThresholdCriterionStateMixin(BelowThresholdCriterionStatusesMixin, CriterionStateMixin):
    criterion_patch_exclusion_check = False


class BelowThresholdCriterionState(BelowThresholdCriterionStateMixin, BelowThresholdTenderState):
    pass
