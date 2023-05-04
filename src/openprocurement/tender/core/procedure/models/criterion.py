from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.types import StringType, MD5Type, IntType
from openprocurement.api.context import get_now
from openprocurement.api.models import (
    Reference,
    Period,
    Model,
    IsoDateTimeType,
    ListType,
    Classification as BaseClassification,
)
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import (
    CRITERION_REQUIREMENT_STATUSES_FROM,
    RELEASE_GUARANTEE_CRITERION_FROM,
    GUARANTEE_ALLOWED_TENDER_TYPES,
)

from openprocurement.tender.core.constants import (
    CRITERION_LIFE_CYCLE_COST_IDS,
    AWARD_CRITERIA_LIFE_CYCLE_COST,
)
from openprocurement.tender.core.validation import (
    validate_value_type,
    validate_requirement_values,
)
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.identifier import LegislationIdentifier
from openprocurement.tender.core.procedure.models.base import validate_object_id_uniq
from logging import getLogger


LOGGER = getLogger(__name__)


class CriterionClassification(BaseClassification):
    description = StringType()

    def validate_id(self, data, code):
        tender = get_tender()
        self._validate_guarantee_id(code, tender)
        self._validate_lcc_id(code, tender)

    @staticmethod
    def _validate_guarantee_id(code, tender):
        tender_created = get_first_revision_date(tender, default=get_now())
        criteria_to_check = ("CRITERION.OTHER.CONTRACT.GUARANTEE", "CRITERION.OTHER.BID.GUARANTEE")
        if (
            tender_created >= RELEASE_GUARANTEE_CRITERION_FROM
            and code in criteria_to_check
            and tender["procurementMethodType"] not in GUARANTEE_ALLOWED_TENDER_TYPES
        ):
            raise ValidationError(u"{} is available only in {}".format(code, GUARANTEE_ALLOWED_TENDER_TYPES))

    @staticmethod
    def _validate_lcc_id(code, tender):
        if (
            code in CRITERION_LIFE_CYCLE_COST_IDS
            and tender["awardCriteria"] != AWARD_CRITERIA_LIFE_CYCLE_COST
        ):
            raise ValidationError(f"{code} is available only with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")


class LegislationItem(Model):
    version = StringType()
    identifier = ModelType(LegislationIdentifier, required=True)
    type = StringType(choices=["NATIONAL_LEGISLATION"], default="NATIONAL_LEGISLATION")
    article = StringType()


class ExtendPeriod(Period):
    maxExtendDate = IsoDateTimeType()
    durationInDays = IntType()
    duration = StringType()


class BaseEligibleEvidence(Model):
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


class EligibleEvidence(BaseEligibleEvidence):
    id = MD5Type(required=True, default=lambda: uuid4().hex)

    def validate_relatedDocument(self, data, document_reference):
        if document_reference:
            tender = get_tender()
            if document_reference.id not in [document["id"] for document in tender.get("documents", [])]:
                raise ValidationError("relatedDocument.id should be one of tender documents")


class PatchEligibleEvidence(BaseEligibleEvidence):
    type = StringType(choices=["document", "statement"])


# ---- Requirement

class ReqStatuses:
    ACTIVE = "active"
    CANCELLED = "cancelled"
    DEFAULT = ACTIVE


class BaseRequirement(Model):
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    dataType = StringType(required=True,
                          choices=["string", "number", "integer", "boolean", "date-time"],
                          default="boolean")
    minValue = StringType()
    maxValue = StringType()
    period = ModelType(ExtendPeriod)
    eligibleEvidences = ListType(
        ModelType(EligibleEvidence, required=True),
        default=list,
        validators=[validate_object_id_uniq],
    )
    relatedFeature = MD5Type()
    expectedValue = StringType()
    status = StringType(choices=[
        ReqStatuses.ACTIVE,
        ReqStatuses.CANCELLED,
    ], default=ReqStatuses.DEFAULT)


class PostRequirement(BaseRequirement):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    datePublished = IsoDateTimeType()

    def validate_minValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("minValue must be integer or number")
            validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("maxValue must be integer or number")
            validate_value_type(value, data['dataType'])

    def validate_expectedValue(self, data, value):
        if value:
            validate_value_type(value, data['dataType'])

    def validate_relatedFeature(self, data, feature_id):
        if feature_id:
            tender = get_tender()
            features = [] if not tender.get("features") else tender.get("features")
            if feature_id not in [feature.id for feature in features]:
                raise ValidationError("relatedFeature should be one of features")

    @serializable(serialized_name="status", serialize_when_none=False)
    def set_status(self):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > CRITERION_REQUIREMENT_STATUSES_FROM:
            return self.status or ReqStatuses.DEFAULT

    @serializable(serialized_name="datePublished", serialize_when_none=False)
    def set_datePublished(self):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > CRITERION_REQUIREMENT_STATUSES_FROM:
            return self.datePublished.isoformat() if self.datePublished else get_now().isoformat()


class PatchRequirement(BaseRequirement):
    title = StringType(min_length=1)
    dataType = StringType(
        choices=["string", "number", "integer", "boolean", "date-time"],
    )
    status = StringType(choices=[ReqStatuses.ACTIVE, ReqStatuses.CANCELLED])


class PatchExclusionLccRequirement(Model):
    status = StringType(choices=[ReqStatuses.ACTIVE, ReqStatuses.CANCELLED])
    eligibleEvidences = ListType(
        ModelType(EligibleEvidence, required=True),
        default=list,
        validators=[validate_object_id_uniq],
    )


class PutRequirement(PatchRequirement):
    status = StringType(choices=[ReqStatuses.ACTIVE, ReqStatuses.CANCELLED])


class PutExclusionLccRequirement(PatchExclusionLccRequirement):
    status = StringType(choices=[ReqStatuses.ACTIVE, ReqStatuses.CANCELLED])


class RequirementForeign(PostRequirement):
    dateModified = IsoDateTimeType()


class Requirement(RequirementForeign):
    status = StringType(choices=[
        ReqStatuses.ACTIVE,
        ReqStatuses.CANCELLED,
    ])

# ---- Requirement


# ---- Requirement Group
class BaseRequirementGroup(Model):
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    requirements = ListType(ModelType(
        RequirementForeign,
        required=True,
        validators=[validate_requirement_values]
    ), min_size=1)


class RequirementGroup(BaseRequirementGroup):
    id = MD5Type(required=True, default=lambda: uuid4().hex)


class PatchRequirementGroup(BaseRequirementGroup):
    pass

# Requirement Group ----


# ---- Criterion
class BaseCriterion(Model):
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    source = StringType(choices=["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"])
    relatesTo = StringType(choices=["tenderer", "item", "lot", "tender"])
    relatedItem = MD5Type()
    classification = ModelType(CriterionClassification, required=True)


class Criterion(BaseCriterion):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    additionalClassifications = ListType(ModelType(BaseClassification, required=True))
    legislation = ListType(ModelType(LegislationItem, required=True))
    requirementGroups = ListType(
        ModelType(RequirementGroup, required=True),
        required=True,
        min_size=1,
        validators=[validate_object_id_uniq],
    )

    def validate_relatesTo(self, data, value):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > RELEASE_GUARANTEE_CRITERION_FROM:
            if not value:
                raise ValidationError("This field is required.")

        if data.get("classification") and data["classification"]["id"] in CRITERION_LIFE_CYCLE_COST_IDS:
            if not tender.get("lots") and value != "tender":
                raise ValidationError(
                    f"{data['classification']['id']} criteria relatesTo should be `tender` if tender has no lots"
                )

            if tender.get("lots") and value != "lot":
                raise ValidationError(
                    f"{data['classification']['id']} criteria relatesTo should be `lot` if tender has lots"
                )

    def validate_relatedItem(self, data, value):
        if not value and data.get("relatesTo") in ["item", "lot"]:
            raise ValidationError("This field is required.")

        is_criterion_active = not data.get("requirementGroups") or any(
            req.get("status", "active") == "active"
            for rg in data.get("requirementGroups", "")
            for req in rg.get("requirements", "")
        )

        if value and is_criterion_active:
            tender = get_tender()
            if data.get("relatesTo") == "lot":
                lot_ids = [i["id"] for i in tender.get("lots") or []]
                if value not in lot_ids:
                    raise ValidationError("relatedItem should be one of lots")
            if data.get("relatesTo") == "item":
                item_ids = [i["id"] for i in tender.get("items") or []]
                if value not in item_ids:
                    raise ValidationError("relatedItem should be one of items")

    def validate_requirementGroups(self, data, requirement_groups: list):
        for rg in requirement_groups:
            requirements = rg.get("requirements", "")
            if not requirements:
                return
            for requirement in requirements:
                validate_requirement(data, requirement)


class PatchCriterion(BaseCriterion):
    title = StringType(min_length=1)
    classification = ModelType(CriterionClassification)

# Criterion ----


def validate_criteria_requirement_id_uniq(criteria, *_) -> None:
    if criteria:
        req_ids = [req["id"] for c in criteria for rg in c["requirementGroups"] for req in rg["requirements"]]
        if get_first_revision_date(get_tender(), default=get_now()) > CRITERION_REQUIREMENT_STATUSES_FROM:
            req_ids = [req["id"]
                       for c in criteria
                       for rg in c["requirementGroups"]
                       for req in rg["requirements"] if req["status"] == ReqStatuses.DEFAULT]
        if req_ids and len(set(req_ids)) != len(req_ids):
            raise ValidationError("Requirement id should be uniq for all requirements in tender")


# TODO: should to write on this cases for work with requirement and requirement_groups
def validate_requirement(criterion: dict, requirement: dict) -> None:
    validate_requirement_dataType(criterion, requirement)
    validate_requirement_expectedValue(criterion, requirement)
    validate_requirement_eligibleEvidences(criterion, requirement)


def validate_requirement_dataType(criterion: dict, requirement: dict) -> None:
    classification = criterion["classification"]
    if (
        classification.get("id")
        and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE")
        and requirement.get("dataType") != "boolean"
    ):
        raise ValidationError([{"dataType": ["dataType must be boolean"]}])


def validate_requirement_expectedValue(criterion: dict, requirement: dict) -> None:
    valid_value = False
    expected_value = requirement.get("expectedValue")
    if expected_value:
        valid_value = validate_value_type(expected_value, requirement['dataType'])

    classification = criterion["classification"]
    if (
        classification["id"]
        and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE")
        and valid_value is not True
    ):
        raise ValidationError([{"expectedValue": ["Value must be true"]}])


def validate_requirement_eligibleEvidences(criterion: dict, requirement: dict) -> None:
    if requirement.get("eligibleEvidences"):
        classification = criterion["classification"]
        if classification["id"] and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE"):
            raise ValidationError([{"eligibleEvidences": ["This field is forbidden for current criterion"]}])


def validate_requirement(criterion: dict, requirement: dict) -> None:
    validate_requirement_dataType(criterion, requirement)
    validate_requirement_expectedValue(criterion, requirement)
    validate_requirement_eligibleEvidences(criterion, requirement)


def validate_requirement_dataType(criterion: dict, requirement: dict) -> None:
    classification = criterion["classification"]
    if (
        classification.get("id")
        and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE")
        and requirement.get("dataType") != "boolean"
    ):
        raise ValidationError([{"dataType": ["dataType must be boolean"]}])


def validate_requirement_expectedValue(criterion: dict, requirement: dict) -> None:
    valid_value = False
    expected_value = requirement.get("expectedValue")
    if expected_value:
        valid_value = validate_value_type(expected_value, requirement['dataType'])

    classification = criterion["classification"]
    if (
        classification["id"]
        and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE")
        and valid_value is not True
    ):
        raise ValidationError([{"expectedValue": ["Value must be true"]}])


def validate_requirement_eligibleEvidences(criterion: dict, requirement: dict) -> None:
    if requirement.get("eligibleEvidences"):
        classification = criterion["classification"]
        if classification["id"] and classification["id"].startswith("CRITERION.OTHER.BID.LANGUAGE"):
            raise ValidationError([{"eligibleEvidences": ["This field is forbidden for current criterion"]}])
