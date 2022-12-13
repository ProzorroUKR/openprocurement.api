from openprocurement.api.utils import error_handler
from schematics.exceptions import ValidationError
from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.models.req_response import validate_evidence_relatedDocument, validate_evidence_type


class ReqResponseEvidenceState(BaseState):
    parent_obj_name: str

    def always(self, data: dict) -> None:
        self.pre_save_validations(data)

    def pre_save_validations(self, data: dict) -> None:
        req_response = self.request.validated["requirement_response"]

        try:
            self.validate_evidence_data(req_response, data)
        except ValidationError as e:
            error_name = list(e.messages[0].keys())[0]
            error_msg = e.messages[0][error_name]
            self.request.errors.status = 422
            self.request.errors.add("body", error_name, error_msg)
            raise error_handler(self.request)

    def validate_evidence_data(self, req_response: dict, evidence: dict) -> None:
        parent = self.request.validated[self.parent_obj_name]
        validate_evidence_relatedDocument(parent, evidence, self.parent_obj_name)
        validate_evidence_type(req_response, evidence)


class BidReqResponseEvidenceState(ReqResponseEvidenceState):
    parent_obj_name = "bid"

    def pre_save_validate(self, data: dict) -> None:
        bid = self.request.validated["bid"]
        if bid["status"] not in ["active", "pending"]:
            return
        super(BidReqResponseEvidenceState, self).pre_save_validate(data)


class AwardReqResponseEvidenceState(ReqResponseEvidenceState):
    parent_obj_name = "award"


class QualificationReqResponseEvidenceState(ReqResponseEvidenceState):
    parent_obj_name = "qualification"
