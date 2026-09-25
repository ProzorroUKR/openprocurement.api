from schematics.exceptions import ValidationError

from openprocurement.api.constants_env import (
    RELEASE_ECRITERIA_ARTICLE_17,
    REQ_RESPONSE_VALUES_VALIDATION_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.api.validation import validate_tender_first_revision_date
from openprocurement.tender.core.procedure.models.req_response import (
    MatchResponseValue,
    PatchRequirementResponse,
    RequirementResponse,
    validate_req_response_evidences_relatedDocument,
    validate_req_response_related_tenderer,
    validate_req_response_requirement,
    validate_response_requirement_uniq,
)
from openprocurement.tender.core.procedure.state.utils import invalidate_pending_bid
from openprocurement.tender.core.procedure.validation import (
    validate_req_response_values,
)


class BaseReqResponseState(BaseState):
    post_data_model = RequirementResponse
    patch_data_model = PatchRequirementResponse
    data_model = RequirementResponse

    # the owner (bid / tender) that may change the responses, and the roles exempt from it per method
    req_response_owner_item_name = "tender"
    req_response_owner_exempt_roles: dict = {
        "POST": ("Administrator",),
        "PATCH": ("Administrator",),
        "DELETE": ("Administrator",),
    }
    # the object and its statuses in which the responses can be changed
    req_response_status_object = "tender"
    req_response_allowed_statuses: tuple = ("draft", "draft.pending", "draft.stage2", "active.tendering")
    # bid: an active 24h milestone allows the changes regardless of the tender status
    req_response_milestone_24_skip = False
    # bid: the responses are hidden until the auction
    req_response_view_check = False

    def validate_req_response_get_request(self):
        if self.req_response_view_check:
            self.validate_req_response_view_allowed()

    def validate_req_response_post_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_operation_allowed()
        self.validate_input_data(self.get_post_data_model(), allow_bulk=True)

    def validate_req_response_patch_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_operation_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "requirement_response")

    def validate_req_response_delete_request(self):
        self.validate_req_response_owner()
        self.validate_req_response_operation_allowed()

    def validate_req_response_owner(self):
        if self.request.authenticated_role not in self.req_response_owner_exempt_roles.get(self.request.method, ()):
            self.validate_item_owner(self.req_response_owner_item_name)

    def validate_req_response_operation_allowed(self):
        if self.req_response_milestone_24_skip and self.allowed_by_qualification_milestone_24():
            return
        self.validate_ecriteria_object_status(self.req_response_status_object, self.req_response_allowed_statuses)

    def validate_ecriteria_object_status(self, obj_name, valid_statuses):
        request = self.request
        validate_tender_first_revision_date(request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
        current_status = request.validated[obj_name]["status"]
        if current_status not in valid_statuses:
            raise_operation_error(
                request,
                "Can't {} object if {} not in {} statuses".format(
                    request.method.lower(), obj_name, list(valid_statuses)
                ),
            )

    def allowed_by_qualification_milestone_24(self):
        now = get_request_now().isoformat()
        tender = get_tender()
        bid_id = self.request.validated["bid"]["id"]
        if "qualifications" in tender:  # for procedures with pre-qualification
            qualifications = [q for q in tender["qualifications"] if q["status"] == "pending" and q["bidID"] == bid_id]
        else:
            qualifications = [q for q in tender.get("awards", "") if q["status"] == "pending" and q["bid_id"] == bid_id]
        for q in qualifications:
            for milestone in q.get("milestones", ""):
                if milestone["code"] == "24h" and milestone["date"] <= now <= milestone["dueDate"]:
                    return True
        return False

    def validate_req_response_view_allowed(self):
        tender = get_tender()
        pre_qualification_tenders = (
            "aboveThresholdEU",
            "competitiveDialogueUA",
            "competitiveDialogueEU",
            "competitiveDialogueEU.stage2",
            "esco",
            "closeFrameworkAgreementUA",
        )
        if tender["procurementMethodType"] in pre_qualification_tenders:
            invalid_tender_statuses = ("active.tendering",)
        else:
            invalid_tender_statuses = ("active.tendering", "active.auction")
        if tender["status"] in invalid_tender_statuses:
            raise_operation_error(
                self.request,
                f"Can't view {'bid' if self.request.matchdict.get('bid_id') else 'bids'} "
                f"in current ({tender['status']}) tender status",
            )

    def always(self, data: dict) -> None:
        self.pre_save_validations(data)

    def pre_save_validations(self, data: dict) -> None:
        parent = self.request.validated[self.parent_obj_name]

        if isinstance(data, dict):
            data = [data]

        def add_error(error_name: str, e: ValidationError) -> None:
            error_msg = e.messages[0]
            if self.request.method != "POST":
                # For operation with concrete requirement response
                if isinstance(e.messages[0], dict):
                    error_name = list(e.messages[0].keys())[0]
                    error_msg = e.messages[0][error_name]
                else:
                    error_name = "data"
                    error_msg = e.messages[0]

            self.request.errors.add("body", error_name, error_msg)

        try:
            validate_response_requirement_uniq(parent.get("requirementResponses"))
        except ValidationError as e:
            add_error("requirementResponses", e)

        for i, req_response in enumerate(data):
            try:
                self.validate_req_response_data(parent, req_response)
            except ValidationError as e:
                add_error(f"requirementResponses.{i}", e)

        if self.request.errors:
            self.request.errors.status = 422
            raise error_handler(self.request)

    def validate_req_response_data(self, parent: dict, req_response: dict) -> None:
        validate_req_response_requirement(req_response, self.parent_obj_name)
        MatchResponseValue.match(req_response, parent_data=parent)
        validate_req_response_related_tenderer(parent, req_response)
        validate_req_response_evidences_relatedDocument(parent, req_response, self.parent_obj_name)
        if get_request_now() > REQ_RESPONSE_VALUES_VALIDATION_FROM:
            validate_req_response_values(req_response)

    def on_delete(self):
        pass


class BidReqResponseState(BaseReqResponseState):
    req_response_owner_item_name = "bid"
    req_response_milestone_24_skip = True
    req_response_view_check = True
    parent_obj_name = "bid"

    def validate_req_response_data(self, parent: dict, req_response: dict) -> None:
        bid = self.request.validated[self.parent_obj_name]
        if bid["status"] not in ["active", "pending"]:
            return
        super().validate_req_response_data(parent, req_response)

    def always(self, data: dict) -> None:
        super().always(data)
        invalidate_pending_bid()

    def on_delete(self):
        invalidate_pending_bid()


class AwardReqResponseState(BaseReqResponseState):
    req_response_owner_exempt_roles = {"POST": (), "PATCH": (), "DELETE": ("Administrator",)}
    req_response_allowed_statuses = ("active.qualification", "active")
    parent_obj_name = "award"


class QualificationReqResponseState(BaseReqResponseState):
    req_response_status_object = "qualification"
    req_response_allowed_statuses = ("pending",)
    parent_obj_name = "qualification"
