from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.models.criterion import EligibleEvidence, PatchEligibleEvidence
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    BaseCriterionStateMixin,
    RequirementValidationsMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.utils import validation_error_handler
from openprocurement.tender.core.procedure.validation import validate_object_id_uniq


class EligibleEvidenceStateMixin(RequirementValidationsMixin, BaseCriterionStateMixin):
    post_data_model = EligibleEvidence
    patch_data_model = PatchEligibleEvidence
    data_model = EligibleEvidence

    # pq: the tender status is checked on every evidence change
    evidence_status_check_always = False

    def validate_post_request(self):
        self.validate_criterion_owner()
        self.validate_input_data(self.get_post_data_model())

    def validate_patch_request(self):
        self.validate_criterion_owner()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "evidence")

    def validate_delete_request(self):
        self.validate_criterion_owner()

    def evidence_on_post(self, data: dict) -> None:
        self._validate_ids_uniq()
        self.evidence_always(data)

    def evidence_on_patch(self, before: dict, after: dict) -> None:
        self.evidence_always(after)

    def evidence_on_delete(self, data: dict) -> None:
        self.evidence_always(data)

    def evidence_always(self, data: dict) -> None:
        if self.evidence_status_check_always:
            self._validate_operation_criterion_in_tender_status()
        self._validate_change_requirement_objects()
        self._validate_for_language_criterion()
        self.validate_action_with_exist_inspector_review_request()
        self.invalidate_bids()
        self.invalidate_review_requests()

    def _validate_for_language_criterion(self):
        request = get_request()
        classification = request.validated["criterion"]["classification"]
        if classification["id"] and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE"):
            raise_operation_error(request, "Forbidden for current criterion")

    @validation_error_handler
    def _validate_ids_uniq(self) -> None:
        evs = self.request.validated["requirement"]["eligibleEvidences"]
        validate_object_id_uniq(evs, obj_name="eligibleEvidence")


class EligibleEvidenceState(EligibleEvidenceStateMixin, TenderState):
    pass
