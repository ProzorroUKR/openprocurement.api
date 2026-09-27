from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.criterion import EligibleEvidence, PatchEligibleEvidence
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderCriteriaRulesMixin,
    TenderDetailsState,
)


class EligibleEvidenceStateMixin(TenderCriteriaRulesMixin):
    """eligible evidences endpoint: request validation and hooks (the rules are shared with the tender endpoint)"""

    post_data_model = EligibleEvidence
    patch_data_model = PatchEligibleEvidence
    data_model = EligibleEvidence

    # items get their relatedLot through the tender endpoint, in a separate request
    related_lot_in_items_check = False

    def validate_evidence_post_request(self):
        self.validate_criterion_owner()
        self.validate_input_data(self.get_post_data_model())

    def validate_evidence_patch_request(self):
        self.validate_criterion_owner()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "evidence")

    def validate_evidence_delete_request(self):
        self.validate_criterion_owner()

    def evidence_on_post(self, requirement: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def evidence_on_patch(self, before: dict, after: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())

    def evidence_on_delete(self, evidence: dict) -> None:
        self.on_patch(self.request.validated["tender_src"], get_tender())


class EligibleEvidenceState(EligibleEvidenceStateMixin, TenderDetailsState):
    pass
