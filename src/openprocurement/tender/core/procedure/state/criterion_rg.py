from schematics.exceptions import ValidationError
from openprocurement.api.utils import error_handler
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.criterion import BaseCriterionStateMixin
from openprocurement.tender.core.procedure.models.criterion import (
    validate_requirement,
    validate_criteria_requirement_id_uniq,
)
from openprocurement.tender.core.procedure.models.base import validate_object_id_uniq
from openprocurement.tender.core.procedure.state.utils import validation_error_handler


class RequirementGroupStateMixin(BaseCriterionStateMixin):
    def requirement_group_on_post(self, data: dict) -> None:
        self.validate_on_post(data)
        self.requirement_group_always(data)

    def requirement_group_on_patch(self, before: dict, after: dict) -> None:
        self.validate_on_patch(before, after)
        self.requirement_group_always(after)

    def requirement_group_always(self, data: dict) -> None:
        self.invalidate_bids()
        self._validate_requirements_data(data)

    def validate_on_post(self, data: dict) -> None:
        criterion = self.request.validated["criterion"]
        self._validate_operation_criterion_in_tender_status()
        self._validate_patch_exclusion_ecriteria_objects(criterion)
        self._validate_ids_uniq()

    def validate_on_patch(self, before: dict, after: dict) -> None:
        criterion = self.request.validated["criterion"]
        self._validate_operation_criterion_in_tender_status()
        self._validate_patch_exclusion_ecriteria_objects(criterion)

    @validation_error_handler
    def _validate_ids_uniq(self) -> None:
        criteria = self.request.validated["tender"]["criteria"]
        rgs = self.request.validated["criterion"]["requirementGroups"]
        validate_object_id_uniq(rgs, obj_name="requirementGroup")
        validate_criteria_requirement_id_uniq(criteria)

    def _validate_requirements_data(self, data: dict) -> None:
        criterion = self.request.validated["criterion"]
        for req in data.get("requirements", ""):
            try:
                validate_requirement(criterion, req)
            except ValidationError as e:
                self.request.errors.status = 422
                self.request.errors.add("body", "requirements", e.messages)
                raise error_handler(self.request)


class RequirementGroupState(RequirementGroupStateMixin, TenderState):
    pass
