from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.validation import base_validate_operation_ecriteria_objects


class BaseBelowThresholdCriterionStateMixin:
    def _validate_operation_criterion_in_tender_status(self) -> None:
        valid_statuses = ["draft", "active.enquiries"]
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)


class BelowThresholdCriterionStateMixin(BaseBelowThresholdCriterionStateMixin, CriterionStateMixin):

    def validate_on_patch(self, before: dict, after: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_criterion_uniq_patch(before, after)


class BelowThresholdCriterionState(BelowThresholdCriterionStateMixin, BelowThresholdTenderState):
    pass
