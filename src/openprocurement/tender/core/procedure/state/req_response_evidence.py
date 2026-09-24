from schematics.exceptions import ValidationError

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.tender.core.procedure.models.evidence import Evidence, PatchEvidence
from openprocurement.tender.core.procedure.models.req_response import (
    validate_evidence_relatedDocument,
    validate_evidence_type,
)
from openprocurement.tender.core.procedure.state.req_response import BaseReqResponseState
from openprocurement.tender.core.procedure.state.utils import invalidate_pending_bid
from openprocurement.tender.core.procedure.utils import get_criterion_requirement


class ReqResponseEvidenceState(BaseState):
    post_data_model = Evidence
    patch_data_model = PatchEvidence
    data_model = Evidence

    req_response_owner_item_name = BaseReqResponseState.req_response_owner_item_name
    req_response_owner_exempt_roles = BaseReqResponseState.req_response_owner_exempt_roles
    req_response_status_object = BaseReqResponseState.req_response_status_object
    req_response_allowed_statuses = BaseReqResponseState.req_response_allowed_statuses
    req_response_milestone_24_skip = False
    req_response_view_check = False
    validate_get_request = BaseReqResponseState.validate_get_request
    validate_delete_request = BaseReqResponseState.validate_delete_request
    validate_req_response_owner = BaseReqResponseState.validate_req_response_owner
    validate_req_response_operation_allowed = BaseReqResponseState.validate_req_response_operation_allowed
    validate_ecriteria_object_status = BaseReqResponseState.validate_ecriteria_object_status
    allowed_by_qualification_milestone_24 = BaseReqResponseState.allowed_by_qualification_milestone_24
    validate_req_response_view_allowed = BaseReqResponseState.validate_req_response_view_allowed
    parent_obj_name: str

    def validate_post_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_operation_allowed()
        self.validate_input_data(self.get_post_data_model())

    def validate_patch_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_operation_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "evidence")

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

    def on_delete(self):
        pass


class BidReqResponseEvidenceState(ReqResponseEvidenceState):
    req_response_owner_item_name = "bid"
    req_response_milestone_24_skip = True
    req_response_view_check = True
    parent_obj_name = "bid"

    def validate_req_response_operation_allowed(self):
        if self.allowed_by_qualification_milestone_24():
            return
        request = self.request
        tender = get_tender()
        valid_statuses = list(self.req_response_allowed_statuses)
        requirement_id = request.validated["requirement_response"]["requirement"]["id"]
        criterion = get_criterion_requirement(tender, requirement_id)
        if criterion and criterion["source"] == "winner":
            awarded_status = ["active.awarded", "active.qualification"]
            if tender["procurementMethodType"] in ("closeFrameworkAgreementUA",):
                awarded_status.append("active.qualification.stand-still")
            valid_statuses.extend(awarded_status)
            if tender["status"] not in awarded_status:
                raise_operation_error(request, f"available only in {awarded_status} statuses")
            bid_id = request.validated["bid"]["id"]
            active_award = None
            for award in tender.get("awards", ""):
                if award["status"] == "active" and award["bid_id"] == bid_id:
                    active_award = award
                    break
            if active_award is None:
                raise_operation_error(request, "Winner criteria available only with active award")
            current_contract = None
            for contract in tender.get("contracts", ""):
                if contract.get("awardId") == active_award["id"]:
                    current_contract = contract
                    break
            if current_contract and current_contract.status == "pending":
                raise_operation_error(request, "forbidden if contract not in status `pending`")
        self.validate_ecriteria_object_status("tender", valid_statuses)

    def pre_save_validations(self, data: dict) -> None:
        bid = self.request.validated["bid"]
        if bid["status"] not in ["active", "pending"]:
            return
        super().pre_save_validations(data)

    def always(self, data: dict) -> None:
        super().always(data)
        invalidate_pending_bid()

    def on_delete(self):
        invalidate_pending_bid()


class AwardReqResponseEvidenceState(ReqResponseEvidenceState):
    req_response_allowed_statuses = ("active.qualification", "active")
    parent_obj_name = "award"


class QualificationReqResponseEvidenceState(ReqResponseEvidenceState):
    req_response_status_object = "qualification"
    req_response_allowed_statuses = ("pending",)
    parent_obj_name = "qualification"
