from schematics.exceptions import ValidationError

from openprocurement.api.utils import (
    get_first_revision_date,
    get_now,
    error_handler,
)
from openprocurement.api.validation import _validate_tender_first_revision_date
from openprocurement.api.constants import CRITERION_REQUIREMENT_STATUSES_FROM
from openprocurement.tender.core.constants import CRITERION_LIFE_CYCLE_COST_IDS
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import base_validate_operation_ecriteria_objects
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.criterion import BaseCriterionStateMixin
from openprocurement.tender.core.procedure.models.criterion import validate_requirement, validate_criteria_requirement_id_uniq
from openprocurement.tender.core.procedure.state.utils import validation_error_handler


class RequirementValidationsMixin:
    def _validate_change_requirement_objects(self) -> None:
        valid_statuses = ["draft", "draft.pending", "draft.stage2"]
        tender = get_tender()
        tender_creation_date = get_first_revision_date(tender, default=get_now())
        criterion = self.request.validated["criterion"]
        if (
                tender_creation_date < CRITERION_REQUIREMENT_STATUSES_FROM
                or criterion["classification"]["id"] in CRITERION_LIFE_CYCLE_COST_IDS
        ):
            valid_statuses.append("active.tendering")
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)


class RequirementStateMixin(RequirementValidationsMixin, BaseCriterionStateMixin):
    def requirement_on_post(self, data: dict) -> None:
        self.validate_on_post(data)
        self.requirement_always(data)

    def requirement_on_patch(self, before: dict, after: dict) -> None:
        self.validate_on_patch(before, after)
        self.requirement_always(after)

    def requirement_on_put(self, before: dict, after: dict) -> None:
        self.validate_on_put(before, after)
        self.requirement_always(after)

    def requirement_always(self, data: dict) -> None:
        self.invalidate_bids()
        self.validate_always(data)

    def validate_on_post(self, data: dict) -> None:
        criterion = self.request.validated["criterion"]
        self._validate_operation_criterion_in_tender_status()
        self._validate_patch_exclusion_ecriteria_objects(criterion)
        self._validate_ids_uniq()

    def validate_on_patch(self, before: dict, after: dict) -> None:
        self._validate_change_requirement_objects()

    def validate_on_put(self, before: dict, after: dict) -> None:
        self._validate_put_requirement_objects()

    def validate_always(self, data: dict) -> None:
        self._validate_requirement_data(data)

    @validation_error_handler
    def _validate_ids_uniq(self) -> None:
        criteria = self.request.validated["tender"]["criteria"]
        validate_criteria_requirement_id_uniq(criteria)

    def _validate_put_requirement_objects(self) -> None:
        _validate_tender_first_revision_date(self.request, validation_date=CRITERION_REQUIREMENT_STATUSES_FROM)
        valid_statuses = ["active.tendering"]
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)

    @validation_error_handler
    def _validate_requirement_data(self, data: dict) -> None:
        criterion = self.request.validated["criterion"]
        validate_requirement(criterion, data)


class RequirementState(RequirementStateMixin, TenderState):
    pass
