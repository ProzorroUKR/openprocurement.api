# -*- coding: utf-8 -*-
from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.types import MD5Type, IntType
from openprocurement.api.models import (
    Model,
    Period,
    IsoDateTimeType,
    ListType,
    Reference,
)
from schematics.types import StringType
from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    RELEASE_ECRITERIA_ARTICLE_17,
    CRITERION_REQUIREMENT_STATUSES_FROM,
)
from openprocurement.tender.core.procedure.validation import (
    validate_value_type,
)
from openprocurement.tender.core.procedure.context import get_tender, get_bid, get_json_data
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.models.base import (
    BaseBid,
    validate_object_id_uniq,
)
from openprocurement.tender.core.models import (
    BaseAward, QualificationMilestoneListMixin,
    validate_response_requirement_uniq,
)
from logging import getLogger

LOGGER = getLogger(__name__)
DEFAULT_REQUIREMENT_STATUS = "active"


class ExtendPeriod(Period):
    maxExtendDate = IsoDateTimeType()
    durationInDays = IntType()
    duration = StringType()


# ECriteria
class EligibleEvidence(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    type = StringType(
        choices=["document", "statement"],
        default="statement"
    )
    relatedDocument = ModelType(Reference)

    def validate_relatedDocument(self, data, document_reference):
        if document_reference:
            tender = get_tender()
            if not any(d and document_reference.id == d["id"] for d in tender.get("documents")):
                raise ValidationError("relatedDocument.id should be one of tender documents")


class Evidence(EligibleEvidence):

    def validate_relatedDocument(self, data, document_reference):
        if bid_in_invalid_status():
            return

        if data["type"] in ["document"] and not document_reference:
            raise ValidationError("This field is required.")

    def validate_type(self, data, value):
        if bid_in_invalid_status():
            return

        parent = data["__parent__"]
        requirement_reference = parent.requirement
        requirement, *_ = get_requirement_obj(requirement_reference.id)
        if requirement:
            evidences_type = [i["type"] for i in requirement.get("eligibleEvidences", "")]
            if evidences_type and value not in evidences_type:
                raise ValidationError("type should be one of eligibleEvidences types")


class RequirementResponse(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
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

    def validate_relatedItem(self, data, relatedItem):
        if relatedItem is None or bid_in_invalid_status():
            return

        tender = get_tender()
        if not any(i and relatedItem == i["id"] for i in tender.get("items")):
            raise ValidationError("relatedItem should be one of items")

    def validate_relatedTenderer(self, data, relatedTenderer):
        if bid_in_invalid_status():
            return

        parent = data["__parent__"]
        if relatedTenderer and isinstance(parent, Model):
            if relatedTenderer.id not in [
                organization.identifier.id
                for organization in parent.get("tenderers", "")
            ]:
                raise ValidationError("relatedTenderer should be one of bid tenderers")

    def validate_evidences(self, data, evidences):
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

    def validate_requirement(self, data, requirement_ref):
        if bid_in_invalid_status():
            return

        # Finding out what the f&#ck is going on
        # parent is mist be Bid
        requirement_ref_id = requirement_ref.get("id")

        # now we use requirement_ref.id to find something in this Bid
        requirement, _, criterion = get_requirement_obj(requirement_ref_id)
        # well this function above only use parent to check if it's Model (???)
        # then it takes Tender.criteria.requirementGroups.requirements
        # finds one with exact "id" and "not default status"
        if not requirement:
            raise ValidationError("requirement should be one of criteria requirements")

        # looks at criterion.source
        # and decides if our requirement_ref actually can be provided by Bid
        # (in this case, also seems this validation can be reused in BaseAward, QualificationMilestoneListMixin)
        source_map = {
            "procuringEntity": (BaseAward, QualificationMilestoneListMixin),
            "tenderer": BaseBid,
            "winner": BaseBid,
        }
        parent = data["__parent__"]
        source = criterion['source']
        available_parents = source_map.get(source)
        if available_parents and not isinstance(parent, available_parents):
            raise ValidationError(f"Requirement response in {parent.__class__.__name__} can't have requirement "
                                  f"criteria with source: {source}")
        return requirement_ref

    def validate_value(self, data, value):
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
def bid_in_invalid_status():
    status = get_json_data().get("status")
    if not status:
        bid = get_bid()
        if bid:
            status = bid["status"]
        else:
            status = "active"
    return status in ("deleted", "invalid", "invalid.pre-qualification", "unsuccessful", "draft")


def get_requirement_obj(requirement_id):
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


def get_criterion_requirement(tender, requirement_id):
    for criteria in tender.get("criteria", ""):
        for group in criteria.get("requirementGroups", ""):
            for req in group.get("requirements", ""):
                if req["id"] == requirement_id:
                    return criteria


# --- UTILS
# requirementResponses mixin ---
def is_doc_id_in_container(bid, container_name, doc_id):
    documents = bid.get(container_name)
    if isinstance(documents, list):
        return any(d["id"] == doc_id for d in documents)


class PatchBidResponsesMixin(Model):
    requirementResponses = ListType(
        ModelType(RequirementResponse, required=True),
        validators=[validate_object_id_uniq, validate_response_requirement_uniq],
    )


class PostBidResponsesMixin(PatchBidResponsesMixin):
    """
    this model is used to update "full" data during patch and post requests
    """
    def validate_selfEligible(self, data, value):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > RELEASE_ECRITERIA_ARTICLE_17:
            if value is not None:
                raise ValidationError("Rogue field.")
        elif value is None:
            raise ValidationError("This field is required.")

    def validate_requirementResponses(self, data, requirement_responses):
        tender = get_tender()
        tender_created = get_first_revision_date(tender, default=get_now())

        if tender_created < RELEASE_ECRITERIA_ARTICLE_17:
            if requirement_responses:
                raise ValidationError("Rogue field.")
            return

        if data["status"] not in ["active", "pending"]:
            return

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

        # validating relatedDocument.id
        for response in requirement_responses or "":
            for evidence in response.get("evidences", ""):
                related_doc = evidence.get("relatedDocument")
                if related_doc:
                    doc_id = related_doc["id"]
                    if (
                            not is_doc_id_in_container(data, "documents", doc_id) and
                            not is_doc_id_in_container(data, "financialDocuments", doc_id) and
                            not is_doc_id_in_container(data, "eligibilityDocuments", doc_id) and
                            not is_doc_id_in_container(data, "qualificationDocuments", doc_id)
                    ):
                        raise ValidationError([{
                            "evidences": [{"relatedDocument": ["relatedDocument.id should be one of bid documents"]}]
                        }])


# --- requirementResponses mixin
