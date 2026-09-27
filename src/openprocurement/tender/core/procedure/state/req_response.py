from schematics.exceptions import ValidationError

from openprocurement.api.constants_env import (
    RELEASE_ECRITERIA_ARTICLE_17,
    REQ_RESPONSE_VALUES_VALIDATION_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import validate_tender_first_revision_date
from openprocurement.tender.core.procedure.context import get_bid
from openprocurement.tender.core.procedure.models.req_response import (
    MatchResponseValue,
    PatchRequirementResponse,
    RequirementResponse,
    validate_bid_requirement_responses_coverage,
    validate_evidence_relatedDocument,
    validate_evidence_type,
    validate_req_response_evidences_relatedDocument,
    validate_req_response_related_tenderer,
    validate_req_response_requirement,
    validate_response_requirement_uniq,
)
from openprocurement.tender.core.procedure.state.utils import diff_items
from openprocurement.tender.core.procedure.utils import get_criterion_requirement
from openprocurement.tender.core.procedure.validation import (
    validate_req_response_values,
)


class RequirementResponsesRulesMixin(BaseState):
    """
    requirementResponses of a bid / award / qualification: the same rules for the parent object endpoint
    and for the responses endpoints (/requirement_responses and their evidences), which apply their change
    to the parent object and run its patch hooks (requirement_responses_parent_on_patch)
    """

    # the object holding the responses (its documents / tenderers are referenced by the responses)
    requirement_responses_parent_obj_name: str
    # the responses are checked for a parent object in these statuses only (a draft may be incomplete)
    requirement_responses_checked_statuses: tuple = ("active", "pending")
    # every criterion with source tenderer / winner must be answered (bid)
    requirement_responses_coverage_check = False
    # the responses endpoints: the roles exempt from the ownership check per method, and the owned object
    req_response_owner_exempt_roles: dict = {
        "POST": ("Administrator",),
        "PATCH": ("Administrator",),
        "DELETE": ("Administrator",),
    }
    req_response_owner_item = "tender"

    def validate_requirement_responses_change(self, before: dict, after: dict) -> None:
        """
        All responses are checked when the parent object enters a status (creation, activation), the added /
        changed ones on a later change. The responses themselves and the criteria coverage are checked for a
        parent object in the checked statuses only, the value / values consistency (between them) - in any status.
        """
        responses = after.get("requirementResponses") or []
        if before.get("status") != after.get("status"):
            checked_responses, checked_evidences = responses, []
        else:
            diff = diff_items(before.get("requirementResponses") or [], responses, "evidences")
            if not diff:
                return
            checked_responses = diff.added + diff.changed_after
            # evidences changed in a response that is otherwise unchanged (a checked response covers its evidences)
            checked_evidences = []
            for response_before, response in diff.nested:
                if response in checked_responses:
                    continue
                evidences = diff_items(response_before.get("evidences") or [], response.get("evidences") or [], "")
                checked_evidences.extend((response, evidence) for evidence in evidences.added + evidences.changed_after)
        errors = []
        try:
            validate_response_requirement_uniq(responses)
        except ValidationError as e:
            errors.extend(e.messages)
        if errors:
            raise_operation_error(self.request, errors, status=422, name="requirementResponses")
        checked_status = after.get("status") in self.requirement_responses_checked_statuses
        if checked_status:
            for response in checked_responses:
                try:
                    self.validate_requirement_response(after, response)
                except ValidationError as e:
                    errors.extend(e.messages)
            for response, evidence in checked_evidences:
                try:
                    self.validate_requirement_response_evidence(after, response, evidence)
                except ValidationError as e:
                    errors.extend(e.messages)
            if errors:
                raise_operation_error(self.request, errors, status=422, name="requirementResponses")
        if get_request_now() > REQ_RESPONSE_VALUES_VALIDATION_FROM:
            for response in checked_responses:
                validate_req_response_values(response)
        if checked_status and self.requirement_responses_coverage_check and self.request.method != "DELETE":
            # a response can be deleted from an active bid to switch the requirement group
            # (the documented 24h flow): the coverage is checked on the next change of the responses
            try:
                validate_bid_requirement_responses_coverage(after, responses)
            except ValidationError as e:
                raise_operation_error(self.request, e.messages, status=422, name="requirementResponses")

    def validate_requirement_response(self, parent: dict, response: dict) -> None:
        parent_obj_name = self.requirement_responses_parent_obj_name
        validate_req_response_requirement(response, parent_obj_name)
        MatchResponseValue.match(response, parent_data=parent)
        validate_req_response_related_tenderer(parent, response)
        validate_req_response_evidences_relatedDocument(parent, response, parent_obj_name)
        for evidence in response.get("evidences") or []:
            validate_evidence_type(response, evidence)

    def validate_requirement_response_evidence(self, parent: dict, response: dict, evidence: dict) -> None:
        validate_evidence_relatedDocument(parent, evidence, self.requirement_responses_parent_obj_name)
        validate_evidence_type(response, evidence)

    # --- the responses endpoints ---

    def validate_req_response_get_request(self):
        pass

    def validate_req_response_evidence_get_request(self):
        pass

    def validate_req_response_owner(self):
        if self.request.authenticated_role not in self.req_response_owner_exempt_roles.get(self.request.method, ()):
            self.validate_item_owner(self.req_response_owner_item)

    def validate_req_response_operation_allowed(self):
        raise NotImplementedError

    def validate_req_response_evidence_operation_allowed(self):
        self.validate_req_response_operation_allowed()

    def validate_req_response_object_status(self, obj_name: str, valid_statuses: tuple | list) -> None:
        validate_tender_first_revision_date(self.request, validation_date=RELEASE_ECRITERIA_ARTICLE_17)
        current_status = self.request.validated[obj_name]["status"]
        if current_status not in valid_statuses:
            raise_operation_error(
                self.request,
                "Can't {} object if {} not in {} statuses".format(
                    self.request.method.lower(), obj_name, list(valid_statuses)
                ),
            )

    def requirement_responses_parent_on_patch(self):
        """runs the parent object patch hooks with the change applied by a responses endpoint"""
        raise NotImplementedError


class BidRequirementResponsesRulesMixin(RequirementResponsesRulesMixin):
    """the requirement responses of a bid (see RequirementResponsesRulesMixin)"""

    requirement_responses_parent_obj_name = "bid"
    requirement_responses_coverage_check = True
    req_response_owner_item = "bid"
    # tender statuses in which the responses can be changed on the responses endpoints
    # (an active 24h milestone allows it regardless)
    req_response_allowed_tender_statuses: tuple = ("draft", "draft.pending", "draft.stage2", "active.tendering")

    def validate_req_response_get_request(self):
        self.validate_bid_get_request()

    def validate_req_response_evidence_get_request(self):
        self.validate_bid_get_request()

    def validate_req_response_operation_allowed(self):
        if self.bid_allowed_by_qualification_milestone_24():
            return
        self.validate_req_response_object_status("tender", self.req_response_allowed_tender_statuses)

    def validate_req_response_evidence_operation_allowed(self):
        """the evidences of a winner criterion response are changed by the winner after the award"""
        if self.bid_allowed_by_qualification_milestone_24():
            return
        request = self.request
        tender = get_tender()
        valid_statuses = list(self.req_response_allowed_tender_statuses)
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
        self.validate_req_response_object_status("tender", valid_statuses)

    def requirement_responses_parent_on_patch(self):
        self.on_patch(self.request.validated["bid_src"], get_bid())


class AwardRequirementResponsesRulesMixin(RequirementResponsesRulesMixin):
    """the requirement responses of an award (see RequirementResponsesRulesMixin)"""

    requirement_responses_parent_obj_name = "award"
    req_response_owner_exempt_roles: dict = {"POST": (), "PATCH": (), "DELETE": ("Administrator",)}
    # tender statuses in which the responses can be changed on the responses endpoints
    req_response_allowed_tender_statuses: tuple = ("active.qualification", "active")

    def validate_req_response_operation_allowed(self):
        self.validate_req_response_object_status("tender", self.req_response_allowed_tender_statuses)

    def requirement_responses_parent_on_patch(self):
        award_src, award = self.request.validated["award_src"], self.request.validated["award"]
        self.validate_award_patch(award_src, award)
        self.award_on_patch(award_src, award)


class QualificationRequirementResponsesRulesMixin(RequirementResponsesRulesMixin):
    """the requirement responses of a qualification (see RequirementResponsesRulesMixin)"""

    requirement_responses_parent_obj_name = "qualification"
    # qualification statuses in which the responses can be changed on the responses endpoints
    req_response_allowed_qualification_statuses: tuple = ("pending",)

    def validate_req_response_operation_allowed(self):
        self.validate_req_response_object_status("qualification", self.req_response_allowed_qualification_statuses)

    def requirement_responses_parent_on_patch(self):
        self.qualification_on_patch(
            self.request.validated["qualification_src"], self.request.validated["qualification"]
        )


class ReqResponseStateMixin(RequirementResponsesRulesMixin):
    """
    requirement responses endpoint of a bid / award / qualification: request validation and hooks

    The rules are shared with the parent object endpoint: the hooks run the parent patch hooks with the
    change applied, so both endpoints validate the responses identically.
    """

    post_data_model = RequirementResponse
    patch_data_model = PatchRequirementResponse
    data_model = RequirementResponse

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

    def req_response_on_post(self, req_responses: list) -> None:
        self.requirement_responses_parent_on_patch()

    def req_response_on_patch(self, before: dict, after: dict) -> None:
        self.requirement_responses_parent_on_patch()

    def req_response_on_delete(self, req_response: dict) -> None:
        self.requirement_responses_parent_on_patch()
