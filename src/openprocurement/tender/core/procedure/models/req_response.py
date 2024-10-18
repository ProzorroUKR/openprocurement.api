from logging import getLogger
from typing import List, Optional, Tuple
from uuid import uuid4

from schematics.exceptions import ConversionError, ValidationError
from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.constants import (
    CRITERION_REQUIREMENT_STATUSES_FROM,
    RELEASE_ECRITERIA_ARTICLE_17,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.reference import Reference
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.tender.core.procedure.models.criterion import ReqStatuses
from openprocurement.tender.core.procedure.models.evidence import Evidence
from openprocurement.tender.core.procedure.utils import (
    bid_in_invalid_status,
    get_criterion_requirement,
    tender_created_after,
    tender_created_before,
)
from openprocurement.tender.core.procedure.validation import (
    TYPEMAP,
    validate_object_id_uniq,
    validate_value_type,
)
from openprocurement.tender.pricequotation.constants import PQ

LOGGER = getLogger(__name__)


class ExtendPeriod(Period):
    maxExtendDate = IsoDateTimeType()
    durationInDays = IntType()
    duration = StringType()


# ECriteria


class BaseRequirementResponse(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    period = ModelType(ExtendPeriod)
    requirement = ModelType(Reference, required=True)
    relatedTenderer = ModelType(Reference)
    relatedItem = MD5Type()
    evidences = ListType(
        ModelType(Evidence, required=True),
        default=[],
        validators=[validate_object_id_uniq],
    )

    value = BaseType()
    values = ListType(BaseType(required=True))

    def convert_value(self):
        if self.requirement:
            requirement, *_ = get_requirement_obj(self.requirement.id)
            if requirement:
                return TYPEMAP[requirement["dataType"]](self.value) if self.value else None
        return self.value

    def convert_values(self):
        if self.requirement:
            requirement, *_ = get_requirement_obj(self.requirement.id)
            if requirement:
                return [TYPEMAP[requirement["dataType"]](value) for value in self.values] if self.values else None
        return self.values

    @serializable(serialized_name="value", serialize_when_none=False)
    def serialize_value(self):
        return self.convert_value()

    @serializable(serialized_name="values", serialize_when_none=False)
    def serialize_values(self):
        return self.convert_values()

    def validate_value(self, data, value):
        if value and data.get("requirement"):
            requirement, *_ = get_requirement_obj(data["requirement"]["id"])
            if requirement:
                validate_value_type(value, requirement["dataType"])

    def validate_values(self, data, values):
        if values and data.get("requirement"):
            requirement, *_ = get_requirement_obj(data["requirement"]["id"])
            if requirement:
                for value in values:
                    validate_value_type(value, requirement["dataType"])


class PatchRequirementResponse(BaseRequirementResponse):
    requirement = ModelType(Reference)


class RequirementResponse(BaseRequirementResponse):
    id = MD5Type(required=True, default=lambda: uuid4().hex)

    def validate_relatedItem(self, data: dict, relatedItem: str) -> None:
        if relatedItem is None or bid_in_invalid_status():
            return

        tender = get_tender()
        if not any(i and relatedItem == i["id"] for i in tender.get("items")):
            raise ValidationError("relatedItem should be one of items")

    def validate_evidences(self, data: dict, evidences: List[dict]) -> None:
        if bid_in_invalid_status():
            return
        if not evidences:
            return
        tender = get_tender()
        guarantee_criterion = "CRITERION.OTHER.CONTRACT.GUARANTEE"
        criterion = get_criterion_requirement(tender, data["requirement"].id)

        # should work only for bids !!
        if criterion and criterion["classification"]["id"].startswith(guarantee_criterion):
            valid_statuses = ["active.awarded", "active.qualification"]
            if tender["status"] not in valid_statuses:
                raise ValidationError("available only in {} status".format(valid_statuses))

        for evidence in evidences:
            validate_evidence_type(data, evidence)


# UTILS ---


def get_requirement_obj(
    requirement_id: str,
    tender: dict = None,
) -> Tuple[Optional[dict], Optional[dict], Optional[dict]]:
    if not tender:
        tender = get_tender()
    for criteria in tender.get("criteria", ""):
        for group in criteria.get("requirementGroups", ""):
            for req in reversed(group.get("requirements", "")):
                if req["id"] == requirement_id:
                    if (
                        tender_created_after(CRITERION_REQUIREMENT_STATUSES_FROM)
                        and req.get("status", ReqStatuses.DEFAULT) != ReqStatuses.ACTIVE
                    ):
                        continue
                    return req, group, criteria
    return None, None, None


# --- UTILS

# Validations ---


def validate_req_response_requirement(req_response: dict, parent_obj_name: str = "bid") -> None:
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


def validate_req_response_related_tenderer(parent_data: dict, req_response: dict) -> None:
    related_tenderer = req_response.get("relatedTenderer")

    if related_tenderer and related_tenderer["id"] not in [
        organization["identifier"]["id"] for organization in parent_data.get("tenderers", "")
    ]:
        raise ValidationError([{"relatedTenderer": ["relatedTenderer should be one of bid tenderers"]}])


def validate_req_response_evidences_relatedDocument(
    parent_data: dict,
    req_response: dict,
    parent_obj_name: str,
) -> None:
    for evidence in req_response.get("evidences", ""):
        error = validate_evidence_relatedDocument(parent_data, evidence, parent_obj_name, raise_error=False)
        if error:
            raise ValidationError([{"evidences": error}])


def validate_evidence_relatedDocument(
    parent_data: dict,
    evidence: dict,
    parent_obj_name: str,
    raise_error: bool = True,
) -> List[dict]:
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


def validate_evidence_type(req_response_data: dict, evidence: dict) -> None:
    requirement_reference = req_response_data["requirement"]
    requirement, *_ = get_requirement_obj(requirement_reference["id"])
    if requirement:
        evidences_type = [i["type"] for i in requirement.get("eligibleEvidences", "")]
        value = evidence.get("type")
        if evidences_type and value not in evidences_type:
            raise ValidationError([{"type": ["type should be one of eligibleEvidences types"]}])


def validate_response_requirement_uniq(requirement_responses):
    if requirement_responses:
        req_ids = [i["requirement"]["id"] for i in requirement_responses]
        if any(i for i in set(req_ids) if req_ids.count(i) > 1):
            raise ValidationError([{"requirement": "Requirement id should be uniq for all requirement responses"}])


class MatchResponseValue:
    @classmethod
    def _match_expected_value(cls, datatype, requirement, value):
        expected_value = requirement.get("expectedValue")
        if expected_value:
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
                f"Value {value} is lower then minimal required {min_value} in requirement {requirement['id']}"
            )
        if max_value is not None and value > datatype.to_native(max_value):
            raise ValidationError(
                f"Value {value} is higher then required {max_value} in requirement {requirement['id']}"
            )

    @staticmethod
    def _hack_for_values_with_string_numbers(values):
        # TODO: remove
        def fix_string_numbers(value):
            if isinstance(value, str):
                try:
                    return str(float(value))
                except ValueError:
                    pass
            return value

        return [fix_string_numbers(value) for value in values]

    @classmethod
    def _match_expected_values(cls, datatype, requirement, values):
        expected_min_items = requirement.get("expectedMinItems")
        expected_max_items = requirement.get("expectedMaxItems")
        expected_values = requirement.get("expectedValues", [])
        expected_values = {datatype.to_native(i) for i in expected_values}

        # TODO: remove
        expected_values = cls._hack_for_values_with_string_numbers(expected_values)
        values = cls._hack_for_values_with_string_numbers(values)

        if expected_min_items is not None and expected_min_items > len(values):
            raise ValidationError(
                f"Count of items lower then minimal required {expected_min_items} "
                f"in requirement {requirement['id']}"
            )

        if expected_max_items is not None and expected_max_items < len(values):
            raise ValidationError(
                f"Count of items higher then maximum required {expected_max_items} "
                f"in requirement {requirement['id']}"
            )

        if expected_values and not set(values).issubset(set(expected_values)):
            raise ValidationError(f"Values are not in requirement {requirement['id']}")

    @classmethod
    def match(cls, response):
        requirement, *_ = get_requirement_obj(response["requirement"]["id"])

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
            cls._match_expected_values(datatype, requirement, values)


# --- Validations


# Bid requirementResponses mixin ---
def is_doc_id_in_container(bid: dict, container_name: str, doc_id: str):
    documents = bid.get(container_name)
    if isinstance(documents, list):
        return any(d["id"] == doc_id for d in documents)


class PatchObjResponsesMixin(Model):
    requirementResponses = ListType(
        ModelType(RequirementResponse, required=True),
        validators=[validate_object_id_uniq, validate_response_requirement_uniq],
    )


class ObjResponseMixin(PatchObjResponsesMixin):
    def validate_requirementResponses(self, data: dict, requirement_responses: Optional[List[dict]]) -> None:
        requirement_responses = requirement_responses or []

        if tender_created_before(RELEASE_ECRITERIA_ARTICLE_17):
            if requirement_responses:
                raise ValidationError("Rogue field.")
            return

        validation_statuses = ["pending", "active"]
        if get_tender()["procurementMethodType"] in (PQ,):
            validation_statuses.append("draft")

        if data["status"] not in validation_statuses:
            return

        parent_obj_name = self.__name__.lower()
        for name in ["award", "qualification", "bid"]:
            if name in parent_obj_name:
                parent_obj_name = name
                break

        # Validation requirement_response data
        for response in requirement_responses:
            validate_req_response_requirement(response, parent_obj_name=parent_obj_name)
            MatchResponseValue.match(response)
            validate_req_response_related_tenderer(data, response)
            validate_req_response_evidences_relatedDocument(data, response, parent_obj_name=parent_obj_name)


class PostBidResponsesMixin(ObjResponseMixin):
    """
    this model is used to update "full" data during patch and post requests
    """

    def validate_selfEligible(self, data: dict, value: Optional[bool]):
        if tender_created_after(RELEASE_ECRITERIA_ARTICLE_17):
            if value is not None:
                raise ValidationError("Rogue field.")
        elif value is None:
            raise ValidationError("This field is required.")

    def validate_requirementResponses(self, data: dict, requirement_responses: Optional[List[dict]]) -> None:
        requirement_responses = requirement_responses or []

        if tender_created_before(RELEASE_ECRITERIA_ARTICLE_17):
            if requirement_responses:
                raise ValidationError("Rogue field.")
            return

        validation_statuses = ["pending", "active"]
        if get_tender()["procurementMethodType"] in (PQ,):
            validation_statuses.append("draft")

        if data["status"] not in validation_statuses:
            return

        # Validation requirement_response data
        for response in requirement_responses:
            validate_req_response_requirement(response)
            MatchResponseValue.match(response)
            validate_req_response_related_tenderer(data, response)
            validate_req_response_evidences_relatedDocument(data, response, parent_obj_name="bid")

        tender = get_tender()

        # Lists for criteria ids that failed validation
        missed_full_criteria_ids = []
        multiple_group_criteria_ids = []
        missed_partial_criteria_ids = []

        # Get all answered requirements
        all_answered_requirements_ids = [i["requirement"]["id"] for i in requirement_responses]

        # Iterate criteria
        for criteria in tender.get("criteria", []):
            # Skip criteria for not existing lots (probably)

            if criteria.get("relatesTo") in ("lot", "item"):
                if criteria.get("relatesTo") == "item":
                    item = [item for item in tender.get("items", "") if item["id"] == criteria["relatedItem"]][0]
                    related_lot = item.get("relatedLot")
                else:
                    related_lot = criteria["relatedItem"]

                for lotVal in data.get("lotValues", ""):
                    if related_lot == lotVal["relatedLot"]:
                        break
                else:
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
                "Responses are required for all criteria with source tenderer, "
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


# --- requirementResponses mixin
