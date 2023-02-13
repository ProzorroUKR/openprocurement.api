from openprocurement.api.utils import get_first_revision_date, get_now
from openprocurement.api.constants import CRITERION_REQUIREMENT_STATUSES_FROM
from openprocurement.tender.belowthreshold.procedure.state.criterion import BaseBelowThresholdCriterionStateMixin
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.validation import (
    base_validate_operation_ecriteria_objects,
    _validate_tender_first_revision_date,
)


class BelowThresholdRequirementValidationsMixin:
    def _validate_change_requirement_objects(self) -> None:
        valid_statuses = ["draft"]
        tender = get_tender()
        tender_creation_date = get_first_revision_date(tender, default=get_now())
        if tender_creation_date < CRITERION_REQUIREMENT_STATUSES_FROM:
            valid_statuses.append("active.enquiries")
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)


class BelowThresholdRequirementStateMixin(
    BelowThresholdRequirementValidationsMixin,
    BaseBelowThresholdCriterionStateMixin,
    RequirementStateMixin,
):
    pass


class BelowThresholdRequirementState(BelowThresholdRequirementStateMixin, BelowThresholdTenderState):

    def validate_on_post(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_ids_uniq()

    def _validate_put_requirement_objects(self) -> None:
        _validate_tender_first_revision_date(self.request, validation_date=CRITERION_REQUIREMENT_STATUSES_FROM)
        valid_statuses = ["active.enquiries"]
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)
