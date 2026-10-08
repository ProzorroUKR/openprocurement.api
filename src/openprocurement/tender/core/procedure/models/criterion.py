from enum import StrEnum
from logging import getLogger
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.constants import (
    COUNTRIES_MAP,
    LANGUAGE_CODES,
)
from openprocurement.api.constants_env import (
    CRITERION_REQUIREMENT_STATUSES_FROM,
    PQ_CRITERIA_ID_FROM,
)
from openprocurement.api.context import get_json_data, get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import (
    Classification as BaseClassification,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.reference import Reference
from openprocurement.api.procedure.models.unit import Unit as BaseUnit
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.constants import (
    ReqStatuses,
)
from openprocurement.tender.core.procedure.models.identifier import (
    LegislationIdentifier,
)
from openprocurement.tender.core.procedure.validation import (
    TYPEMAP,
    validate_object_id_uniq,
    validate_value_type,
)
from openprocurement.tender.pricequotation.constants import PQ

LOGGER = getLogger(__name__)


class ValidateIdMixing(Model):
    id = StringType(required=True, default=lambda: uuid4().hex)

    def validate_id(self, data, value):
        tender = get_tender() or get_json_data()
        if (
            tender.get("procurementMethodType") in (PQ,)
            and get_first_revision_date(tender, default=get_request_now()) <= PQ_CRITERIA_ID_FROM
        ):
            return
        field = MD5Type()
        value = field.to_native(value)
        field.validate(value)


class CriterionClassification(BaseClassification):
    description = StringType()


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
    type = StringType(choices=["document", "statement"], default="statement")
    relatedDocument = ModelType(Reference)


class EligibleEvidence(BaseEligibleEvidence):
    id = MD5Type(required=True, default=lambda: uuid4().hex)


class PatchEligibleEvidence(BaseEligibleEvidence):
    type = StringType(choices=["document", "statement"])


# ---- Requirement


class Unit(BaseUnit):
    name = StringType(required=True)


class DataSchema(StrEnum):
    ISO_639 = "ISO 639-3"
    ISO_3166 = "ISO 3166-1 alpha-2"


ISO_MAPPING = {
    DataSchema.ISO_639.value: LANGUAGE_CODES,
    DataSchema.ISO_3166.value: COUNTRIES_MAP.keys(),
}


class BaseRequirement(Model):
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    dataType = StringType(
        required=True,
        choices=["string", "number", "integer", "boolean", "date-time"],
        default="boolean",
    )
    period = ModelType(ExtendPeriod)
    eligibleEvidences = ListType(
        ModelType(EligibleEvidence, required=True),
        default=list,
        validators=[validate_object_id_uniq],
    )
    relatedFeature = MD5Type()
    status = StringType(
        choices=[
            ReqStatuses.ACTIVE,
            ReqStatuses.CANCELLED,
        ],
        default=ReqStatuses.DEFAULT,
    )
    unit = ModelType(Unit)
    dataSchema = StringType(
        choices=[
            DataSchema.ISO_639.value,
            DataSchema.ISO_3166.value,
        ],
    )

    minValue = BaseType()
    maxValue = BaseType()
    expectedValue = BaseType()

    expectedValues = ListType(BaseType(required=True), min_size=1)
    expectedMinItems = IntType(min_value=1)
    expectedMaxItems = IntType(min_value=1)


class PostRequirement(ValidateIdMixing, BaseRequirement):
    datePublished = IsoDateTimeType()

    @serializable(serialized_name="minValue", serialize_when_none=False)
    def set_minValue(self):
        return TYPEMAP[self.dataType](self.minValue) if self.minValue else None

    @serializable(serialized_name="maxValue", serialize_when_none=False)
    def set_maxValue(self):
        return TYPEMAP[self.dataType](self.maxValue) if self.maxValue else None

    @serializable(serialized_name="expectedValue", serialize_when_none=False)
    def set_expectedValue(self):
        return TYPEMAP[self.dataType](self.expectedValue) if self.expectedValue else None

    @serializable(serialized_name="expectedValues", serialize_when_none=False)
    def set_expectedValues(self):
        return [TYPEMAP[self.dataType](value) for value in self.expectedValues] if self.expectedValues else None

    def validate_minValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("minValue must be integer or number")
            validate_value_type(value, data["dataType"])

    def validate_maxValue(self, data, value):
        if value:
            if data["dataType"] not in ["integer", "number"]:
                raise ValidationError("maxValue must be integer or number")
            validate_value_type(value, data["dataType"])

    def validate_expectedValue(self, data, value):
        if value:
            conflict_fields = ["minValue", "maxValue", "expectedValues"]
            if any(data.get(i) is not None for i in conflict_fields):
                raise ValidationError(f"expectedValue conflicts with {conflict_fields}")

            validate_value_type(value, data["dataType"])

    def validate_expectedValues(self, data, values):
        expected_min_items = data.get("expectedMinItems")
        expected_max_items = data.get("expectedMaxItems")

        if values:
            if not isinstance(values, (list, tuple, set)):
                raise ValidationError("Values should be list")

            conflict_fields = ["minValue", "maxValue", "expectedValue"]
            if any(data.get(i) is not None for i in conflict_fields):
                raise ValidationError(f"expectedValues conflicts with {conflict_fields}")

            for value in values:
                validate_value_type(value, data["dataType"])

            if expected_min_items and expected_max_items and expected_min_items > expected_max_items:
                raise ValidationError("expectedMinItems couldn't be higher then expectedMaxItems")

            if expected_min_items and expected_min_items > len(values):
                raise ValidationError("expectedMinItems couldn't be higher then count of items in expectedValues")

            if expected_max_items and expected_max_items > len(values):
                raise ValidationError("expectedMaxItems couldn't be higher then count of items in expectedValues")

        elif expected_min_items or expected_max_items:
            raise ValidationError("expectedMinItems and expectedMaxItems couldn't exist without expectedValues")

    @serializable(serialized_name="status", serialize_when_none=False)
    def set_status(self):
        tender = get_tender() or get_json_data()
        if get_first_revision_date(tender, default=get_request_now()) < CRITERION_REQUIREMENT_STATUSES_FROM:
            return
        return self.status or ReqStatuses.DEFAULT

    @serializable(serialized_name="datePublished", serialize_when_none=False)
    def set_datePublished(self):
        tender = get_tender() or get_json_data()
        request = get_request()

        if get_first_revision_date(tender, default=get_request_now()) < CRITERION_REQUIREMENT_STATUSES_FROM:
            return

        if request.method == "POST":
            return get_request_now().isoformat()

        return self.datePublished.isoformat() if self.datePublished else get_request_now().isoformat()


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


class PatchTechnicalFeatureRequirement(Model):
    period = ModelType(ExtendPeriod)
    eligibleEvidences = ListType(
        ModelType(EligibleEvidence, required=True),
    )
    relatedFeature = MD5Type()
    status = StringType(
        choices=[
            ReqStatuses.ACTIVE,
            ReqStatuses.CANCELLED,
        ],
        default=ReqStatuses.DEFAULT,
    )

    minValue = BaseType()
    maxValue = BaseType()
    expectedValue = BaseType()

    expectedValues = ListType(BaseType(required=True), min_size=1)
    expectedMinItems = IntType(min_value=1)
    expectedMaxItems = IntType(min_value=1)


class PutRequirement(PatchRequirement):
    status = StringType(choices=[ReqStatuses.ACTIVE, ReqStatuses.CANCELLED])


class PutExclusionLccRequirement(PatchExclusionLccRequirement):
    status = StringType(choices=[ReqStatuses.ACTIVE, ReqStatuses.CANCELLED])


class RequirementForeign(PostRequirement):
    dateModified = IsoDateTimeType()


class Requirement(RequirementForeign):
    status = StringType(
        choices=[
            ReqStatuses.ACTIVE,
            ReqStatuses.CANCELLED,
        ]
    )


# ---- Requirement


# ---- Requirement Group
class BaseRequirementGroup(Model):
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    requirements = ListType(
        ModelType(RequirementForeign, required=True),
        min_size=1,
    )


class RequirementGroup(ValidateIdMixing, BaseRequirementGroup):
    pass


class PatchRequirementGroup(BaseRequirementGroup):
    pass


# Requirement Group ----


# ---- Criterion
class BaseCriterion(Model):
    title = StringType(min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    source = StringType(
        choices=["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"],
        required=True,
    )
    relatesTo = StringType(choices=["tenderer", "item", "lot", "tender"])
    relatedItem = MD5Type()
    classification = ModelType(CriterionClassification, required=True)


class Criterion(ValidateIdMixing, BaseCriterion):
    title = StringType(required=True, min_length=1)
    additionalClassifications = ListType(ModelType(BaseClassification, required=True))
    legislation = ListType(ModelType(LegislationItem, required=True), min_size=1)
    requirementGroups = ListType(
        ModelType(RequirementGroup, required=True),
        required=True,
        min_size=1,
        validators=[
            validate_object_id_uniq,
        ],
    )

    def validate_legislation(self, data, value):
        if data.get("classification", {}).get("id") != "CRITERION.OTHER.CONTRACT.GUARANTEE":
            if not value:
                raise ValidationError("This field is required.")


class PatchCriterion(BaseCriterion):
    source = StringType(choices=["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"])
    classification = ModelType(CriterionClassification)


# Criterion ----
