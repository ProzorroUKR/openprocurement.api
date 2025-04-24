from typing import Callable

from pyramid.request import Request

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.constants import (
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
)
from openprocurement.tender.core.procedure.models.criterion import (
    validate_criteria_requirement_uniq,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.utils import validation_error_handler
from openprocurement.tender.core.procedure.validation import (
    base_validate_operation_ecriteria_objects,
    check_requirements_active,
    validate_object_id_uniq,
)


class BaseCriterionStateMixin:
    request: Request

    tender_valid_statuses = ["draft", "draft.pending", "draft.stage2", "active.tendering"]

    def _validate_operation_criterion_in_tender_status(self) -> None:
        base_validate_operation_ecriteria_objects(self.request, self.tender_valid_statuses)

    def _validate_patch_exclusion_ecriteria_objects(self, before: dict) -> None:
        if before["classification"]["id"].startswith("CRITERION.EXCLUSION"):
            raise_operation_error(self.request, "Can't update exclusion ecriteria objects")

    def invalidate_bids(self) -> None:
        tender = get_tender()
        if hasattr(self, "invalidate_bids_data"):
            self.invalidate_bids_data(tender)

    def validate_tech_feature_localization_criteria(self, data: dict) -> None:
        tender = get_tender()
        if not isinstance(data, list):
            data = [data]

        for criterion in data:
            if criterion["classification"]["id"] in (CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION):
                item = next(
                    (item for item in tender["items"] if item["id"] == criterion.get("relatedItem")),
                    None,
                )
                if not item:
                    raise_operation_error(
                        self.request,
                        f'For {criterion["classification"]["id"]} criteria `relatedItem` should be item from tender',
                        status=422,
                    )
                else:
                    if criterion["classification"]["id"] == CRITERION_TECHNICAL_FEATURES:
                        if not (item.get("category") or item.get("profile")):
                            raise_operation_error(
                                self.request,
                                "For technical feature criteria item should have category or profile",
                                status=422,
                            )
                    elif criterion["classification"]["id"] == CRITERION_LOCALIZATION:
                        if not item.get("category"):
                            raise_operation_error(
                                self.request,
                                "For localization criteria item should have category",
                                status=422,
                            )


class CriterionStateMixin(BaseCriterionStateMixin):
    request: Request

    _validate_criterion_uniq: Callable
    validate_criteria_requirements_rules: Callable
    validate_criteria_classification: Callable
    validate_action_with_exist_inspector_review_request: Callable
    invalidate_review_requests: Callable

    def criterion_on_post(self, data: dict) -> None:
        self.criterion_always(data)
        self._validate_ids_uniq(data)

    def criterion_on_patch(self, before: dict, after: dict) -> None:
        self.validate_on_patch(before, after)
        self.criterion_always(after)

    def criterion_always(self, data: dict) -> None:
        self.validate_action_with_exist_inspector_review_request()
        self.invalidate_bids()
        self.invalidate_review_requests()
        self.validate_tech_feature_localization_criteria(data)
        self.validate_criteria_classification(data)
        self.validate_criteria_requirements_rules(data)

    def validate_on_post(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_criterion_uniq(data, previous_criteria=self.request.validated["tender"]["criteria"])

    def validate_on_patch(self, before: dict, after: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_patch_exclusion_ecriteria_objects(before)
        self._validate_criterion_uniq_patch(before, after)

    @validation_error_handler
    def _validate_ids_uniq(self, data) -> None:
        criteria = self.request.validated["tender"]["criteria"]
        validate_object_id_uniq(criteria, obj_name="Criterion")
        validate_criteria_requirement_uniq(criteria)

    def _validate_criterion_uniq_patch(self, before: dict, after: dict) -> None:
        criteria = get_tender().get("criteria")
        updated_criterion_classification = after.get("classification", {}).get("id", "")

        if updated_criterion_classification == before["classification"]["id"]:
            return

        for existed_criterion in criteria:
            if after.get("relatesTo") == existed_criterion.get("relatesTo") and after.get(
                "relatedItem", ""
            ) == existed_criterion.get("relatedItem", ""):
                if updated_criterion_classification == existed_criterion["classification"]["id"]:
                    if check_requirements_active(existed_criterion):
                        raise_operation_error(self.request, "Criteria are not unique")


class CriterionState(CriterionStateMixin, TenderState):
    pass
