from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class BaseBelowThresholdCriterionStateMixin:
    tender_valid_statuses = ["draft", "active.enquiries"]


class BelowThresholdCriterionStateMixin(BaseBelowThresholdCriterionStateMixin, CriterionStateMixin):
    criterion_patch_exclusion_check = False


class BelowThresholdCriterionState(BelowThresholdCriterionStateMixin, BelowThresholdTenderState):
    pass
