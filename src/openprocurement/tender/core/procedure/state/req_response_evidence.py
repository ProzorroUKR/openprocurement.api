from openprocurement.tender.core.procedure.models.evidence import Evidence, PatchEvidence
from openprocurement.tender.core.procedure.state.req_response import (
    RequirementResponsesRulesMixin,
)


class ReqResponseEvidenceStateMixin(RequirementResponsesRulesMixin):
    """
    requirement response evidences endpoint of a bid / award / qualification: request validation and hooks
    (the rules are the parent object's, see ReqResponseStateMixin)
    """

    post_data_model = Evidence
    patch_data_model = PatchEvidence
    data_model = Evidence

    def validate_req_response_evidence_post_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_evidence_operation_allowed()
        self.validate_input_data(self.get_post_data_model())

    def validate_req_response_evidence_patch_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_evidence_operation_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "evidence")

    def validate_req_response_evidence_delete_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_evidence_operation_allowed()

    def req_response_evidence_on_post(self, evidence: dict) -> None:
        self.requirement_responses_parent_on_patch()

    def req_response_evidence_on_patch(self, before: dict, after: dict) -> None:
        self.requirement_responses_parent_on_patch()

    def req_response_evidence_on_delete(self, evidence: dict) -> None:
        self.requirement_responses_parent_on_patch()
