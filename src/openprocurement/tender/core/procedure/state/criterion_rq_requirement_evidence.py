from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    BaseCriterionStateMixin,
    RequirementValidationsMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.utils import validation_error_handler
from openprocurement.tender.core.procedure.validation import validate_object_id_uniq


class EligibleEvidenceStateMixin(RequirementValidationsMixin, BaseCriterionStateMixin):
    def evidence_on_post(self, data: dict) -> None:
        self._validate_ids_uniq()
        self.evidence_always(data)

    def evidence_on_patch(self, before: dict, after: dict) -> None:
        self.evidence_always(after)

    def evidence_on_delete(self, data: dict) -> None:
        self.evidence_always(data)

    def evidence_always(self, data: dict) -> None:
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
