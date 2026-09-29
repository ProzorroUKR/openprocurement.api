from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.criterion import Criterion, PatchCriterion
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderCriteriaRulesMixin,
    TenderDetailsState,
)


class CriterionStateMixin(TenderCriteriaRulesMixin):
    """
    criteria endpoint: request validation and hooks

    The criteria rules (TenderCriteriaRulesMixin) are shared with the tender endpoint: the hooks apply
    the change to the tender and run the tender on_patch, so both endpoints validate criteria identically.
    """

    post_data_model = Criterion
    patch_data_model = PatchCriterion
    data_model = Criterion

    # items get their relatedLot through the tender endpoint, in a separate request
    related_lot_in_items_check = False
    items_related_lot_check = False
    criteria_error_path_strip = 1

    def validate_criterion_post_request(self):
        self.validate_criterion_request_allowed()
        self.validate_input_data(self.get_post_data_model(), allow_bulk=True)

    def validate_criterion_patch_request(self):
        self.validate_criterion_request_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "criterion")

    def validate_criterion_delete_request(self):
        self.validate_criterion_owner()
        self.validate_criteria_delete_allowed(get_tender())

    def validate_criterion_request_allowed(self):
        self.validate_criterion_owner()
        self.validate_criteria_operation_allowed(get_tender())

    def criterion_on_post(self, criteria: list) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def criterion_on_patch(self, before: dict, after: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def criterion_on_delete(self, criterion: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())


class CriterionState(CriterionStateMixin, TenderDetailsState):
    pass
