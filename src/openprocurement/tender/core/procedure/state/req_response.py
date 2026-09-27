from typing import List

from schematics.exceptions import ConversionError, ValidationError

from openprocurement.api.constants_env import (
    CRITERION_REQUIREMENT_STATUSES_FROM,
    RELEASE_ECRITERIA_ARTICLE_17,
    REQ_RESPONSE_VALUES_VALIDATION_FROM,
)
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import validate_tender_first_revision_date
from openprocurement.tender.core.constants import CRITERION_LOCALIZATION, CRITERION_TECHNICAL_FEATURES, ReqStatuses
from openprocurement.tender.core.procedure.context import get_bid
from openprocurement.tender.core.procedure.models.req_response import (
    PatchRequirementResponse,
    RequirementResponse,
    validate_response_requirement_uniq,
)
from openprocurement.tender.core.procedure.state.utils import diff_items
from openprocurement.tender.core.procedure.utils import (
    get_criterion_requirement,
    get_requirement_obj,
    tender_created_after,
    tender_created_before,
)
from openprocurement.tender.core.procedure.validation import TYPEMAP


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
        if responses and tender_created_before(RELEASE_ECRITERIA_ARTICLE_17):
            raise_operation_error(self.request, ["Rogue field."], status=422, name="requirementResponses")
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
                self.validate_response_values(response)
        if checked_status:
            try:
                self.validate_requirement_responses_coverage(after, responses)
            except ValidationError as e:
                raise_operation_error(self.request, e.messages, status=422, name="requirementResponses")

    def validate_requirement_response(self, parent: dict, response: dict) -> None:
        self.validate_response_requirement(response)
        self.validate_response_related_item(response)
        self.match_response_value(response, parent_data=parent)
        self.validate_response_related_tenderer(parent, response)
        self.validate_response_evidences_allowed(response)
        self.validate_response_evidences_related_document(parent, response)
        for evidence in response.get("evidences") or []:
            self.validate_evidence_type(response, evidence)

    def validate_requirement_response_evidence(self, parent: dict, response: dict, evidence: dict) -> None:
        self.validate_response_evidences_allowed(response)
        self.validate_evidence_related_document(parent, evidence)
        self.validate_evidence_type(response, evidence)

    def validate_response_related_item(self, response: dict) -> None:
        """former RequirementResponse.validate_relatedItem"""
        related_item = response.get("relatedItem")
        if related_item is None:
            return
        if not any(i and related_item == i["id"] for i in get_tender().get("items")):
            raise ValidationError([{"relatedItem": ["relatedItem should be one of items"]}])

    def validate_response_evidences_allowed(self, response: dict) -> None:
        """former RequirementResponse.validate_evidences: evidences of a winner criterion come after the award"""
        if not response.get("evidences"):
            return
        tender = get_tender()
        criterion = get_criterion_requirement(tender, response["requirement"]["id"])
        if criterion and criterion["source"] == "winner":
            # active.pre-qualification added in CS-20110
            valid_statuses = ["active.awarded", "active.qualification", "active.pre-qualification"]
            if tender["procurementMethodType"] in ("closeFrameworkAgreementUA",):
                valid_statuses.append("active.qualification.stand-still")
            if tender["status"] not in valid_statuses:
                raise ValidationError([{"evidences": ["available only in {} status".format(valid_statuses)]}])

    def validate_requirement_responses_coverage(self, parent: dict, responses: list) -> None:
        """the bid checks that every criterion is answered; awards and qualifications have no such rule"""

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

    def validate_response_requirement(self, req_response: dict) -> None:
        parent_obj_name = self.requirement_responses_parent_obj_name
        # Finding out what the f&#ck is going on
        # parent is mist be Bid
        requirement_ref = req_response.get("requirement") or {}
        requirement_ref_id = requirement_ref.get("id")

        # now we use requirement_ref.id to find something in this Bid
        requirement, _, criterion = get_requirement_obj(requirement_ref_id)
        # well this function above only use parent to check if it's Model (???)
        # then it takes Tender.criteria.requirementGroups.requirements
        # finds one with exact "id" and "not default status"
        if not requirement:
            raise ValidationError([{"requirement": ["Requirement should be one of criteria requirements"]}])

        # looks at criterion.source
        # and decides if our requirement_ref actually can be provided by Bid
        # (in this case, also seems this validation can be reused in BaseAward, QualificationMilestoneListMixin)
        source_map = {
            "procuringEntity": ("award", "qualification"),
            "tenderer": ("bid",),
            "winner": ("bid",),
        }
        source = criterion.get("source", "tenderer")
        available_parents = source_map.get(source)
        if available_parents and parent_obj_name.lower() not in available_parents:
            raise ValidationError(
                [
                    {
                        "requirement": [
                            f"Requirement response in {parent_obj_name} "
                            f"can't have requirement criteria with source: {source}"
                        ]
                    }
                ]
            )

    def validate_response_related_tenderer(self, parent_data: dict, req_response: dict) -> None:
        related_tenderer = req_response.get("relatedTenderer")

        if related_tenderer and related_tenderer["id"] not in [
            organization["identifier"]["id"] for organization in parent_data.get("tenderers", "")
        ]:
            raise ValidationError([{"relatedTenderer": ["relatedTenderer should be one of bid tenderers"]}])

    def validate_response_evidences_related_document(self, parent_data: dict, req_response: dict) -> None:
        for evidence in req_response.get("evidences", ""):
            error = self.validate_evidence_related_document(parent_data, evidence, raise_error=False)
            if error:
                raise ValidationError([{"evidences": error}])

    def validate_evidence_related_document(
        self, parent_data: dict, evidence: dict, raise_error: bool = True
    ) -> List[dict]:
        parent_obj_name = self.requirement_responses_parent_obj_name
        related_doc = evidence.get("relatedDocument")
        if related_doc:
            doc_id = related_doc["id"]
            if (
                not is_doc_id_in_container(parent_data, "documents", doc_id)
                and not is_doc_id_in_container(parent_data, "financialDocuments", doc_id)
                and not is_doc_id_in_container(parent_data, "eligibilityDocuments", doc_id)
                and not is_doc_id_in_container(parent_data, "qualificationDocuments", doc_id)
            ):
                error_msg = [{"relatedDocument": [f"relatedDocument.id should be one of {parent_obj_name} documents"]}]
                if not raise_error:
                    return error_msg
                raise ValidationError(error_msg)

    def validate_evidence_type(self, req_response_data: dict, evidence: dict) -> None:
        requirement_reference = req_response_data["requirement"]
        requirement, *_ = get_requirement_obj(requirement_reference["id"])
        if requirement:
            evidences_type = [i["type"] for i in requirement.get("eligibleEvidences", "")]
            value = evidence.get("type")
            if evidences_type and value not in evidences_type:
                raise ValidationError([{"type": ["type should be one of eligibleEvidences types"]}])

    def validate_response_values(self, response):
        requirement, *_ = get_requirement_obj(response["requirement"]["id"])
        if requirement:
            if requirement.get("expectedValues") is not None and response.get("value") is not None:
                raise_operation_error(
                    get_request(),
                    f"only 'values' allowed in response for requirement {requirement['id']}",
                    name="requirementResponses",
                    status=422,
                )
            elif requirement.get("expectedValues") is None and response.get("values") is not None:
                raise_operation_error(
                    get_request(),
                    f"only 'value' allowed in response for requirement {requirement['id']}",
                    name="requirementResponses",
                    status=422,
                )

    @classmethod
    def _match_expected_value(cls, datatype, requirement, value):
        expected_value = requirement.get("expectedValue")
        if expected_value is not None:
            if datatype.to_native(expected_value) != value:
                raise ValidationError(
                    f'Value "{value}" does not match expected value "{expected_value}" '
                    f'in requirement {requirement["id"]}'
                )

    @classmethod
    def _match_min_max_value(cls, datatype, requirement, value):
        min_value = requirement.get("minValue")
        max_value = requirement.get("maxValue")

        if min_value is not None and value < datatype.to_native(min_value):
            raise ValidationError(
                f"Value {value} is lower than minimal required {min_value} in requirement {requirement['id']}"
            )
        if max_value is not None and value > datatype.to_native(max_value):
            raise ValidationError(
                f"Value {value} is higher than required {max_value} in requirement {requirement['id']}"
            )

    @classmethod
    def _match_expected_values(cls, datatype, requirement, values, allow_extra_values=False):
        expected_min_items = requirement.get("expectedMinItems")
        expected_max_items = requirement.get("expectedMaxItems")
        expected_values = requirement.get("expectedValues", [])
        expected_values = {datatype.to_native(i) for i in expected_values}
        unique_values = set(values)

        if expected_max_items is not None and expected_max_items < len(unique_values):
            raise ValidationError(
                f"Count of values is higher than maximum of {expected_max_items} "
                f"for requirement {requirement['id']}"
            )

        if allow_extra_values:
            if expected_min_items is not None and expected_min_items > len(unique_values & expected_values):
                raise ValidationError(
                    f"Count of matching values is less than minimum of {expected_min_items} "
                    f"for requirement {requirement['id']}"
                )

        else:
            if expected_min_items is not None and expected_min_items > len(unique_values):
                raise ValidationError(
                    f"Count of values is less than minimum of {expected_min_items} "
                    f"for requirement {requirement['id']}"
                )

            if expected_values and not set(unique_values).issubset(set(expected_values)):
                raise ValidationError(
                    f"One or more values are not among expected values for requirement {requirement['id']}"
                )

    @classmethod
    def match_response_value(cls, response, parent_data=None):
        requirement, _, criterion = get_requirement_obj(response["requirement"]["id"])

        datatype = TYPEMAP[requirement["dataType"]]

        value = response.get("value")
        values = response.get("values")

        if value is None and not values:
            raise ValidationError([{"value": 'Response required at least one of field ["value", "values"]'}])
        if value is not None and values:
            raise ValidationError([{"value": "Field 'value' conflicts with 'values'"}])
        values = [value] if value is not None else values

        if values is not None:
            try:
                values = [datatype.to_native(v) for v in values]
            except ConversionError as e:
                raise ValidationError([{"value": e.messages}])

            for value in values:
                cls._match_expected_value(datatype, requirement, value)
                cls._match_min_max_value(datatype, requirement, value)
            cls._match_expected_values(
                datatype,
                requirement,
                values,
                allow_extra_values=cls._extra_values_allowed(criterion, parent_data),
            )

    @classmethod
    def _extra_values_allowed(cls, criterion, parent_data):
        if not criterion or not parent_data:
            return False

        classification = criterion.get("classification") or {}
        if classification.get("id") not in (CRITERION_TECHNICAL_FEATURES, CRITERION_LOCALIZATION):
            return False

        related_item_id = criterion.get("relatedItem")
        if not related_item_id:
            return False

        return any(
            item.get("id") == related_item_id and item.get("product") for item in (parent_data.get("items") or [])
        )


class BidRequirementResponsesRulesMixin(RequirementResponsesRulesMixin):
    """the requirement responses of a bid (see RequirementResponsesRulesMixin)"""

    requirement_responses_parent_obj_name = "bid"
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

    def validate_requirement_responses_coverage(self, data: dict, requirement_responses: list) -> None:
        """every criterion with source tenderer / winner of the bid lots must be answered, one requirement group per criterion"""
        if self.request.method == "DELETE":
            # a response can be deleted from an active bid to switch the requirement group
            # (the documented 24h flow): the coverage is checked on the next change of the responses
            return

        tender = get_tender()

        # Lists for criteria ids that failed validation
        missed_full_criteria_ids = []
        multiple_group_criteria_ids = []
        missed_partial_criteria_ids = []

        # Get all answered requirements
        all_answered_requirements_ids = [i["requirement"]["id"] for i in requirement_responses]

        # Iterate criteria
        for criteria in tender.get("criteria", []):
            # Initialize variable for lot relation
            related_lot = None

            # Find direct relation to lot
            if criteria.get("relatesTo") == "lot":
                related_lot = criteria["relatedItem"]

            # Find relation to lot through item
            if criteria.get("relatesTo") == "item":
                items = tender.get("items", [])
                item = next((item for item in items if item["id"] == criteria["relatedItem"]), None)
                if item is None:
                    # Non existing item: skip criteria
                    # Should not happen in theory, but happens in practice (i.e. item was deleted)
                    continue
                related_lot = item.get("relatedLot")

            # Skip criteria of lots in which bid is not participating
            if related_lot:
                # Relation to lot is present
                # Check if bid participates in the lot
                for lotVal in data.get("lotValues", ""):
                    if related_lot == lotVal["relatedLot"]:
                        break
                else:
                    # Bid does not participate in the lot
                    # Skip criteria
                    continue

            # Skip non-bid criteria
            if criteria.get("source", "tenderer") not in ("tenderer", "winner"):
                continue

            # Skip criteria that have no active requirements
            if tender_created_after(CRITERION_REQUIREMENT_STATUSES_FROM):
                active_requirements = [
                    requirement
                    for rg in criteria.get("requirementGroups", [])
                    for requirement in rg.get("requirements", [])
                    if requirement.get("status", ReqStatuses.DEFAULT) == ReqStatuses.ACTIVE
                ]
                if not active_requirements:
                    continue

            criteria_ids = {}
            group_answered_requirement_ids = {}

            # Search for answered requirements
            for rg in criteria.get("requirementGroups", []):
                # Get all requirement ids for group
                requirement_ids = {
                    i["id"]
                    for i in rg.get("requirements", [])
                    if i.get("status", ReqStatuses.DEFAULT) != ReqStatuses.CANCELLED
                }

                # Get all answered requirement ids for group
                answered_requirement_ids = {i for i in all_answered_requirements_ids if i in requirement_ids}

                if answered_requirement_ids:
                    group_answered_requirement_ids[rg["id"]] = answered_requirement_ids

                # Save all requirements for each group
                criteria_ids[rg["id"]] = requirement_ids

            if not group_answered_requirement_ids:
                # No answers for this criteria
                missed_full_criteria_ids.append(criteria["id"])
            else:
                # Check if there are multiple groups with answers
                if len(group_answered_requirement_ids) > 1:
                    multiple_group_criteria_ids.append(criteria["id"])

                # Check if all requirements in a group are answered
                rg_id = list(group_answered_requirement_ids.keys())[0]
                if set(criteria_ids[rg_id]).difference(set(group_answered_requirement_ids[rg_id])):
                    missed_partial_criteria_ids.append(criteria["id"])

        if missed_full_criteria_ids:
            raise ValidationError(
                "Responses are required for all criteria with source tenderer/winner, "
                f"failed for criteria {', '.join(missed_full_criteria_ids)}"
            )

        if multiple_group_criteria_ids:
            raise ValidationError(
                "Responses are allowed for only one group of requirements per criterion, "
                f"failed for criteria {', '.join(multiple_group_criteria_ids)}"
            )

        if missed_partial_criteria_ids:
            raise ValidationError(
                "Responses are required for all requirements in a requirement group, "
                f"failed for criteria {', '.join(missed_partial_criteria_ids)}"
            )


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


def is_doc_id_in_container(bid: dict, container_name: str, doc_id: str):
    documents = bid.get(container_name)
    if isinstance(documents, list):
        return any(d["id"] == doc_id for d in documents)
