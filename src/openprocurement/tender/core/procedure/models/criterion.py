from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.types import StringType, MD5Type, IntType
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
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.procedure.models.identifier import LegislationIdentifier
from openprocurement.tender.core.procedure.models.base import validate_object_id_uniq
from logging import getLogger


LOGGER = getLogger(__name__)

DEFAULT_REQUIREMENT_STATUS = "active"


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
            if document_reference.id not in [document["id"] for document in tender.get("documents", [])]:
                raise ValidationError("relatedDocument.id should be one of tender documents")


class Requirement(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
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
    status = StringType(choices=[DEFAULT_REQUIREMENT_STATUS, "cancelled"], default=DEFAULT_REQUIREMENT_STATUS)
    datePublished = IsoDateTimeType()
    dateModified = IsoDateTimeType()

    def validate_minValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("minValue must be integer or number")
            validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("minValue must be integer or number")
            validate_value_type(value, data['dataType'])

    def validate_dataType(self, data, value):
        criterion = data["__parent__"].__parent__
        if criterion.classification.id and criterion.classification.id.startswith("CRITERION.OTHER.BID.LANGUAGE"):
            if value != "boolean":
                raise ValidationError("dataType must be boolean")

    def validate_expectedValue(self, data, value):
        valid_value = False
        if value:
            valid_value = validate_value_type(value, data['dataType'])

        criterion = data["__parent__"].__parent__
        if criterion.classification.id and criterion.classification.id.startswith("CRITERION.OTHER.BID.LANGUAGE"):
            if valid_value is not True:
                raise ValidationError("Value must be true")

    def validate_eligibleEvidences(self, data, value):
        if value:
            criterion = data["__parent__"].__parent__
            if criterion.classification.id and criterion.classification.id.startswith("CRITERION.OTHER.BID.LANGUAGE"):
                raise ValidationError("This field is forbidden for current criterion")

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
            return self.status if self.status else DEFAULT_REQUIREMENT_STATUS

    @serializable(serialized_name="datePublished", serialize_when_none=False)
    def set_datePublished(self):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > CRITERION_REQUIREMENT_STATUSES_FROM:
            return self.datePublished.isoformat() if self.datePublished else get_now().isoformat()


class RequirementGroup(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    requirements = ListType(ModelType(Requirement, required=True, validators=[validate_requirement_values]), min_size=1)


class Criterion(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    source = StringType(choices=["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"])
    relatesTo = StringType(choices=["tenderer", "item", "lot", "tender"])
    relatedItem = MD5Type()
    classification = ModelType(CriterionClassification, required=True)  # TODO: make it required
    additionalClassifications = ListType(ModelType(BaseClassification, required=True))
    legislation = ListType(ModelType(LegislationItem, required=True))
    requirementGroups = ListType(
        ModelType(RequirementGroup, required=True),
        required=True,
        min_size=1,
        validators=[validate_object_id_uniq],
    )

    def _all_requirements_cancelled(self):
        return all(
            requirement.get("status", "") == "cancelled"
            for requirement_group in self.get("requirementGroups", [])
            for requirement in requirement_group.get("requirements", [])
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

        if value:
            tender = get_tender()
            if data.get("relatesTo") == "lot":
                lot_ids = [i["id"] for i in tender.get("lots") or []]
                if value not in lot_ids:
                    raise ValidationError("relatedItem should be one of lots")
            if data.get("relatesTo") == "item":
                item_ids = [i["id"] for i in tender.get("items") or []]
                if value not in item_ids:
                    raise ValidationError("relatedItem should be one of items")


def validate_criteria_requirement_id_uniq(criteria, *args):
    if criteria:
        req_ids = [req.id for c in criteria for rg in c.requirementGroups for req in rg.requirements]
        if get_first_revision_date(get_tender(), default=get_now()) > CRITERION_REQUIREMENT_STATUSES_FROM:
            req_ids = [req.id
                       for c in criteria
                       for rg in c.requirementGroups
                       for req in rg.requirements if req.status == DEFAULT_REQUIREMENT_STATUS]
        if [i for i in set(req_ids) if req_ids.count(i) > 1]:
            raise ValidationError("Requirement id should be uniq for all requirements in tender")
