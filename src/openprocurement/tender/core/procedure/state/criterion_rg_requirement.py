from openprocurement.api.constants import CRITERION_LIFE_CYCLE_COST_IDS
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.constants import CRITERION_TECHNICAL_FEATURES
from openprocurement.tender.core.procedure.models.criterion import (
    PatchRequirement,
    PatchTechnicalFeatureRequirement,
    PostRequirement,
    PutExclusionLccRequirement,
    PutRequirement,
    Requirement,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderCriteriaRulesMixin,
    TenderDetailsState,
)


class RequirementStateMixin(TenderCriteriaRulesMixin):
    """requirements endpoint: request validation and hooks (the rules are shared with the tender endpoint)"""

    post_data_model = PostRequirement
    patch_data_model = PatchRequirement
    put_data_model = PutRequirement
    data_model = Requirement

    # items get their relatedLot through the tender endpoint, in a separate request
    related_lot_in_items_check = False

    def validate_requirement_post_request(self):
        self.validate_criterion_owner()
        self.validate_criteria_operation_allowed(get_tender())
        self.validate_input_data(self.get_post_data_model())

    def validate_requirement_patch_request(self):
        self.validate_criterion_owner()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "requirement")

    def validate_requirement_put_request(self):
        self.validate_criterion_owner()
        self.validate_patch_input_data(self.get_put_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "requirement")
        self.validate_requirement_put_allowed(get_tender())

    def get_patch_data_model(self):
        if not self.requirement_models_by_classification:
            return self.patch_data_model
        criterion = self.request.validated["criterion"]
        classification_id = criterion["classification"]["id"]
        model = PatchRequirement
        if classification_id == CRITERION_TECHNICAL_FEATURES:
            model = PatchTechnicalFeatureRequirement
        return model

    def get_put_data_model(self):
        if not self.requirement_models_by_classification:
            return self.put_data_model
        criterion = self.request.validated["criterion"]
        classification_id = criterion["classification"]["id"]
        model = PutRequirement
        if classification_id.startswith("CRITERION.EXCLUSION") or classification_id in CRITERION_LIFE_CYCLE_COST_IDS:
            model = PutExclusionLccRequirement
        elif classification_id == CRITERION_TECHNICAL_FEATURES:
            model = PatchTechnicalFeatureRequirement
        return model

    def requirement_on_post(self, requirement: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def requirement_on_patch(self, before: dict, after: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def requirement_on_put(self, before: dict, after: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())


class RequirementState(RequirementStateMixin, TenderDetailsState):
    pass
