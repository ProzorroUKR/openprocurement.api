from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.criterion import (
    PatchRequirementGroup,
    RequirementGroup,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderCriteriaRulesMixin,
    TenderDetailsState,
)


class RequirementGroupStateMixin(TenderCriteriaRulesMixin):
    """requirement groups endpoint: request validation and hooks (the rules are shared with the tender endpoint)"""

    post_data_model = RequirementGroup
    patch_data_model = PatchRequirementGroup
    data_model = RequirementGroup

    # items get their relatedLot through the tender endpoint, in a separate request
    related_lot_in_items_check = False
    items_related_lot_check = False
    criteria_error_path_strip = 2

    def validate_requirement_group_post_request(self):
        self.validate_criterion_owner()
        self.validate_criteria_operation_allowed(get_tender())
        self.validate_input_data(self.get_post_data_model())

    def validate_requirement_group_patch_request(self):
        self.validate_criterion_owner()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "requirement_group")

    def requirement_group_on_post(self, requirement_group: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def requirement_group_on_patch(self, before: dict, after: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())


class RequirementGroupState(RequirementGroupStateMixin, TenderDetailsState):
    pass
