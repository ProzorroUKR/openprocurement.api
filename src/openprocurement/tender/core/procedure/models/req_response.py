from typing import Optional, List, Tuple
from logging import getLogger
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import IntType
from schematics.types import MD5Type
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import CRITERION_REQUIREMENT_STATUSES_FROM
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.models import IsoDateTimeType
from openprocurement.api.models import ListType
from openprocurement.api.models import Model
from openprocurement.api.models import Period
from openprocurement.api.models import Reference
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.base import validate_object_id_uniq
from openprocurement.tender.core.procedure.utils import (
    get_first_revision_date,
    get_criterion_requirement,
    bid_in_invalid_status,
)
from openprocurement.tender.core.procedure.models.evidence import Evidence
from openprocurement.tender.core.procedure.validation import (
    validate_value_type,
)

LOGGER = getLogger(__name__)
DEFAULT_REQUIREMENT_STATUS = "active"


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
        default=list(),
        validators=[validate_object_id_uniq],
    )

    value = StringType(required=True)


class PatchRequirementResponse(BaseRequirementResponse):
    requirement = ModelType(Reference)
    value = StringType()
    evidences = ListType(
        ModelType(Evidence, required=True),
        default=list(),
        validators=[validate_object_id_uniq],
    )


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

    def validate_value(self, data: dict, value: str) -> None:
        if bid_in_invalid_status():
            return

        requirement_ref = data.get("requirement")
        if not requirement_ref:
            return

        requirement, *_ = get_requirement_obj(requirement_ref.get("id"))

        if requirement:
            data_type = requirement["dataType"]
            valid_value = validate_value_type(value, data_type)
            expectedValue = requirement.get("expectedValue")
            minValue = requirement.get("minValue")
            maxValue = requirement.get("maxValue")
            if expectedValue and validate_value_type(expectedValue, data_type) != valid_value:
                raise ValidationError("value and requirement.expectedValue must be equal")
            if minValue and valid_value < validate_value_type(minValue, data_type):
                raise ValidationError("value should be higher than eligibleEvidence.minValue")
            if maxValue and valid_value > validate_value_type(maxValue, data_type):
                raise ValidationError("value should be lower than eligibleEvidence.maxValue")


# UTILS ---


def get_requirement_obj(requirement_id: str) -> Tuple[Optional[dict], Optional[dict], Optional[dict]]:
    tender = get_tender()
    tender_creation = get_first_revision_date(tender, default=get_now())
    for criteria in tender.get("criteria", ""):
        for group in criteria.get("requirementGroups", ""):
            for req in reversed(group.get("requirements", "")):
                if req["id"] == requirement_id:
                    if (tender_creation > CRITERION_REQUIREMENT_STATUSES_FROM and
                       req.get("status", DEFAULT_REQUIREMENT_STATUS) != DEFAULT_REQUIREMENT_STATUS):
                        continue
                    return req, group, criteria
    return None, None, None


# --- UTILS

# Validations ---

def validate_req_response_requirement(
        req_response: dict,
        parent_obj_name: str = "bid"
) -> None:

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
        raise ValidationError([{"requirement": ["requirement should be one of criteria requirements"]}])

    # looks at criterion.source
    # and decides if our requirement_ref actually can be provided by Bid
    # (in this case, also seems this validation can be reused in BaseAward, QualificationMilestoneListMixin)
    source_map = {
        "procuringEntity": ("award", "qualification"),
        "tenderer": ("bid",),
        "winner": ("bid",),
    }
    source = criterion.get('source', "tenderer")
    available_parents = source_map.get(source)
    if available_parents and parent_obj_name.lower() not in available_parents:
        raise ValidationError([{
            "requirement": [f"Requirement response in {parent_obj_name} "
                            f"can't have requirement criteria with source: {source}"]
        }])


def validate_req_response_related_tenderer(parent_data: dict, req_response: dict) -> None:

    related_tenderer = req_response.get("relatedTenderer")

    if related_tenderer and related_tenderer["id"] not in [
        organization["identifier"]["id"]
        for organization in parent_data.get("tenderers", "")
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
                not is_doc_id_in_container(parent_data, "documents", doc_id) and
                not is_doc_id_in_container(parent_data, "financialDocuments", doc_id) and
                not is_doc_id_in_container(parent_data, "eligibilityDocuments", doc_id) and
                not is_doc_id_in_container(parent_data, "qualificationDocuments", doc_id)
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
        if any([i for i in set(req_ids) if req_ids.count(i) > 1]):
            raise ValidationError([{"requirement": "Requirement id should be uniq for all requirement responses"}])


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
        tender = get_tender()
        tender_created = get_first_revision_date(tender, default=get_now())

        if tender_created < RELEASE_ECRITERIA_ARTICLE_17:
            if requirement_responses:
                raise ValidationError("Rogue field.")
            return

        if data["status"] not in ["active", "pending"]:
            return

        parent_obj_name = self.__name__.lower()
        for name in ["award", "qualification", "bid"]:
            if name in parent_obj_name:
                parent_obj_name = name
                break
        # Validation requirement_response data
        for response in requirement_responses or "":
            validate_req_response_requirement(response, parent_obj_name=parent_obj_name)
            validate_req_response_related_tenderer(data, response)
            validate_req_response_evidences_relatedDocument(data, response, parent_obj_name=parent_obj_name)


class PostBidResponsesMixin(ObjResponseMixin):
    """
    this model is used to update "full" data during patch and post requests
    """
    def validate_selfEligible(self, data: dict, value: Optional[bool]):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > RELEASE_ECRITERIA_ARTICLE_17:
            if value is not None:
                raise ValidationError("Rogue field.")
        elif value is None:
            raise ValidationError("This field is required.")

    def validate_requirementResponses(self, data: dict, requirement_responses: Optional[List[dict]]) -> None:
        tender = get_tender()
        tender_created = get_first_revision_date(tender, default=get_now())

        if tender_created < RELEASE_ECRITERIA_ARTICLE_17:
            if requirement_responses:
                raise ValidationError("Rogue field.")
            return

        if data["status"] not in ["active", "pending"]:
            return

        # Validation requirement_response data
        for response in requirement_responses or "":
            validate_req_response_requirement(response)
            validate_req_response_related_tenderer(data, response)
            validate_req_response_evidences_relatedDocument(data, response, parent_obj_name="bid")

        all_answered_requirements = [i.requirement.id for i in requirement_responses or ""]
        for criteria in tender.get("criteria", ""):
            if criteria["relatesTo"] == "lot":
                for lotVal in data["lotValues"]:
                    if criteria["relatedItem"] == lotVal["relatedLot"]:
                        break
                else:
                    continue
            if criteria["source"] != "tenderer" and not criteria["classification"]["id"].endswith("GUARANTEE"):
                continue
            if tender_created > CRITERION_REQUIREMENT_STATUSES_FROM:
                active_requirements = [
                    requirement
                    for rg in criteria.get("requirementGroups", "")
                    for requirement in rg.get("requirements", "")
                    if requirement["status"] == "active"
                ]
                if not active_requirements:
                    continue

            criteria_ids = {}
            group_answered_requirement_ids = {}
            for rg in criteria.get("requirementGroups", ""):
                req_ids = {i["id"] for i in rg.get("requirements", "")}
                if tender_created > CRITERION_REQUIREMENT_STATUSES_FROM:
                    req_ids = {i["id"] for i in rg.get("requirements", "") if i["status"] != "cancelled"}
                answered_reqs = {i for i in all_answered_requirements if i in req_ids}

                if answered_reqs:
                    group_answered_requirement_ids[rg["id"]] = answered_reqs
                criteria_ids[rg["id"]] = req_ids

            if not group_answered_requirement_ids:
                raise ValidationError(
                    "Must be answered on all criteria with source `tenderer` and GUARANTEE if declared"
                )

            if len(group_answered_requirement_ids) > 1:
                raise ValidationError("Inside criteria must be answered only one requirement group")

            rg_id = list(group_answered_requirement_ids.keys())[0]
            if set(criteria_ids[rg_id]).difference(set(group_answered_requirement_ids[rg_id])):
                raise ValidationError("Inside requirement group must get answered all of requirements")

# --- requirementResponses mixin
