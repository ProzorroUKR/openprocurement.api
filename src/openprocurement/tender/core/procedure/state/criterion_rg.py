from schematics.exceptions import ValidationError

from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.tender.core.procedure.models.criterion import (
    ReqStatuses,
    validate_criteria_requirement_uniq,
    validate_requirement_eligibleEvidences,
)
from openprocurement.tender.core.procedure.state.criterion import (
    BaseCriterionStateMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.utils import validation_error_handler
from openprocurement.tender.core.procedure.validation import validate_object_id_uniq


class RequirementGroupStateMixin(BaseCriterionStateMixin):
    def requirement_group_on_post(self, data: dict) -> None:
        self.validate_on_post(data)
        self.requirement_group_always(data)
        self.validate_criteria_requirements_rules(self.request.validated["criterion"])
        self.validate_criteria_requirement_from_market(self.request.validated["criterion"])

    def requirement_group_on_patch(self, before: dict, after: dict) -> None:
        self.validate_on_patch(before, after)
        self.requirement_group_always(after)

    def requirement_group_always(self, data: dict) -> None:
        self._validate_reqs_uniq(data)
        self.invalidate_bids()
        self._validate_requirements_data(data)
        self.validate_action_with_exist_inspector_review_request()
        self.invalidate_review_requests()

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
        validate_criteria_requirement_uniq(criteria)

    def _validate_reqs_uniq(self, data) -> None:
        req_titles = [
            req["title"]
            for req in data.get("requirements", [])
            if req.get("status", ReqStatuses.DEFAULT) == ReqStatuses.ACTIVE
        ]
        if len(set(req_titles)) != len(req_titles):
            raise_operation_error(
                self.request,
                "Requirement title should be uniq for one requirementGroup",
                status=422,
            )

    def _validate_requirements_data(self, data: dict) -> None:
        criterion = self.request.validated["criterion"]
        for req in data.get("requirements", ""):
            try:
                validate_requirement_eligibleEvidences(criterion, req)
            except ValidationError as e:
                self.request.errors.status = 422
                self.request.errors.add("body", "requirements", e.messages)
                raise error_handler(self.request)


class RequirementGroupState(RequirementGroupStateMixin, TenderState):
    pass
