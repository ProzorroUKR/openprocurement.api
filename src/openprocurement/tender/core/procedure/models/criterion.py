from enum import StrEnum
from logging import getLogger
from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, field_serializer, field_validator, model_validator

from openprocurement.api.constants import (
    COUNTRIES_MAP,
    LANGUAGE_CODES,
)
from openprocurement.api.constants_env import (
    CRITERION_REQUIREMENT_STATUSES_FROM,
)
from openprocurement.api.context import get_json_data, get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import FieldErrors, ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator, validate_object_id_uniq
from openprocurement.api.procedure.models.item import (
    Classification as BaseClassification,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.reference import Reference
from openprocurement.api.procedure.models.unit import Unit as BaseUnit
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.procedure.value_types import TYPEMAP
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.constants import (
    ReqStatuses,
)
from openprocurement.tender.core.procedure.models.identifier import (
    LegislationIdentifier,
)

LOGGER = getLogger(__name__)


class ValidateIdMixing(Model):
    id: str = Field(default_factory=lambda: uuid4().hex)


class CriterionClassification(BaseClassification):
    description: str | None = None


class LegislationItem(Model):
    version: str | None = None
    identifier: LegislationIdentifier
    type: Literal["NATIONAL_LEGISLATION"] = "NATIONAL_LEGISLATION"
    article: str | None = None


class ExtendPeriod(Period):
    maxExtendDate: IsoDateTime | None = None
    durationInDays: int | None = None
    duration: str | None = None


class BaseEligibleEvidence(Model):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    type: Literal["document", "statement"] = "statement"
    relatedDocument: Reference | None = None


class EligibleEvidence(BaseEligibleEvidence):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)


class PatchEligibleEvidence(BaseEligibleEvidence):
    type: Literal["document", "statement"] | None = None


class Unit(BaseUnit):
    name: str


class DataSchema(StrEnum):
    ISO_639 = "ISO 639-3"
    ISO_3166 = "ISO 3166-1 alpha-2"


ISO_MAPPING = {
    DataSchema.ISO_639.value: LANGUAGE_CODES,
    DataSchema.ISO_3166.value: COUNTRIES_MAP.keys(),
}


class BaseRequirement(Model):
    title: str = Field(min_length=1)
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    dataType: Literal["string", "number", "integer", "boolean", "date-time"] = "boolean"
    period: ExtendPeriod | None = None
    eligibleEvidences: list[EligibleEvidence] = []
    relatedFeature: MD5 | None = None
    status: ReqStatuses = ReqStatuses.DEFAULT
    unit: Unit | None = None
    dataSchema: DataSchema | None = None
    minValue: Any = None
    maxValue: Any = None
    expectedValue: Any = None
    expectedValues: list[Any] | None = Field(None, min_length=1)
    expectedMinItems: int | None = Field(None, ge=1)
    expectedMaxItems: int | None = Field(None, ge=1)

    @field_validator("eligibleEvidences")
    @classmethod
    def validate_eligible_evidences_items(cls, value):
        validate_object_id_uniq(value)
        return value


class PostRequirement(ValidateIdMixing, BaseRequirement):
    datePublished: IsoDateTime | None = None

    @field_serializer("minValue")
    def serialize_min_value(self, value: Any) -> Any:
        return TYPEMAP[self.dataType](value) if value else value

    @field_serializer("maxValue")
    def serialize_max_value(self, value: Any) -> Any:
        return TYPEMAP[self.dataType](value) if value else value

    @field_serializer("expectedValue")
    def serialize_expected_value(self, value: Any) -> Any:
        return TYPEMAP[self.dataType](value) if value else value

    @field_serializer("expectedValues")
    def serialize_expected_values(self, value: Any) -> Any:
        return [TYPEMAP[self.dataType](item) for item in value] if value else value

    @model_validator(mode="after")
    def validate_values(self):
        # all the value fields are checked, the errors are reported together
        errors = {}
        for field, check in (
            ("minValue", self._check_min_max_value),
            ("maxValue", self._check_min_max_value),
            ("expectedValue", self._check_expected_value),
            ("expectedValues", self._check_expected_values),
        ):
            try:
                check(field, getattr(self, field))
            except ValidationError as e:  # ConversionError of the value types as well
                errors[field] = e.messages
        if errors:
            raise FieldErrors(errors)
        return self

    def _check_min_max_value(self, field: str, value: Any) -> None:
        if value:
            if self.dataType not in ["integer", "number"]:
                raise ValidationError(f"{field} must be integer or number")
            validate_value_type(value, self.dataType)

    def _check_expected_value(self, field: str, value: Any) -> None:
        if value:
            conflict_fields = ["minValue", "maxValue", "expectedValues"]
            if any(getattr(self, i) is not None for i in conflict_fields):
                raise ValidationError(f"expectedValue conflicts with {conflict_fields}")
            validate_value_type(value, self.dataType)

    def _check_expected_values(self, field: str, values: Any) -> None:
        expected_min_items = self.expectedMinItems
        expected_max_items = self.expectedMaxItems
        if values:
            if not isinstance(values, (list, tuple, set)):
                raise ValidationError("Values should be list")
            conflict_fields = ["minValue", "maxValue", "expectedValue"]
            if any(getattr(self, i) is not None for i in conflict_fields):
                raise ValidationError(f"expectedValues conflicts with {conflict_fields}")
            for value in values:
                validate_value_type(value, self.dataType)
            if expected_min_items and expected_max_items and expected_min_items > expected_max_items:
                raise ValidationError("expectedMinItems couldn't be higher then expectedMaxItems")
            if expected_min_items and expected_min_items > len(values):
                raise ValidationError("expectedMinItems couldn't be higher then count of items in expectedValues")
            if expected_max_items and expected_max_items > len(values):
                raise ValidationError("expectedMaxItems couldn't be higher then count of items in expectedValues")
        elif expected_min_items or expected_max_items:
            raise ValidationError("expectedMinItems and expectedMaxItems couldn't exist without expectedValues")

    @field_serializer("datePublished")
    def serialize_date_published(self, value: Any) -> Any:
        tender = get_tender() or get_json_data()
        request = get_request()
        if get_first_revision_date(tender, default=get_request_now()) < CRITERION_REQUIREMENT_STATUSES_FROM:
            return value.isoformat() if value else None
        if request.method == "POST":
            return get_request_now().isoformat()
        return value.isoformat() if value else get_request_now().isoformat()


class PatchRequirement(BaseRequirement):
    title: str | None = Field(None, min_length=1)
    dataType: Literal["string", "number", "integer", "boolean", "date-time"] | None = None
    status: ReqStatuses | None = None


class PatchExclusionLccRequirement(Model):
    status: ReqStatuses | None = None
    eligibleEvidences: list[EligibleEvidence] = []

    @field_validator("eligibleEvidences")
    @classmethod
    def validate_eligible_evidences_items(cls, value):
        validate_object_id_uniq(value)
        return value


class PatchTechnicalFeatureRequirement(Model):
    period: ExtendPeriod | None = None
    eligibleEvidences: list[EligibleEvidence] | None = None
    relatedFeature: MD5 | None = None
    status: ReqStatuses = ReqStatuses.DEFAULT
    minValue: Any = None
    maxValue: Any = None
    expectedValue: Any = None
    expectedValues: list[Any] | None = Field(None, min_length=1)
    expectedMinItems: int | None = Field(None, ge=1)
    expectedMaxItems: int | None = Field(None, ge=1)


class PutRequirement(PatchRequirement):
    status: ReqStatuses | None = None


class PutExclusionLccRequirement(PatchExclusionLccRequirement):
    status: ReqStatuses | None = None


class RequirementForeign(PostRequirement):
    dateModified: IsoDateTime | None = None


class Requirement(RequirementForeign):
    status: ReqStatuses | None = None


class BaseRequirementGroup(Model):
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    requirements: list[RequirementForeign] | None = Field(None, min_length=1)


class RequirementGroup(ValidateIdMixing, BaseRequirementGroup):
    pass


class PatchRequirementGroup(BaseRequirementGroup):
    pass


class BaseCriterion(Model):
    title: str | None = Field(None, min_length=1)
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    source: Literal["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"]
    relatesTo: Literal["tenderer", "item", "lot", "tender"] | None = None
    relatedItem: MD5 | None = None
    classification: CriterionClassification


class Criterion(ValidateIdMixing, BaseCriterion):
    title: str = Field(min_length=1)
    additionalClassifications: list[BaseClassification] | None = None
    legislation: list[LegislationItem] | None = Field(None, min_length=1)
    requirementGroups: list[RequirementGroup] = Field(min_length=1)

    @model_field_validator("legislation")
    def validate_legislation(self, value):
        if not self.classification or self.classification.id != "CRITERION.OTHER.CONTRACT.GUARANTEE":
            if not value:
                raise ValidationError("This field is required.")

    @field_validator("requirementGroups")
    @classmethod
    def validate_requirement_groups_items(cls, value):
        validate_object_id_uniq(value)
        return value


class PatchCriterion(BaseCriterion):
    source: Literal["tenderer", "buyer", "procuringEntity", "ssrBot", "winner"] | None = None
    classification: CriterionClassification | None = None


def validate_value_factory(type_map):
    def validator(value, datatype):
        if value is None:
            return
        type_ = type_map.get(datatype)
        if not type_:
            raise ValidationError("Type mismatch: value {} does not confront type {}".format(value, type_))
        return type_(value)

    return validator


validate_value_type = validate_value_factory(TYPEMAP)
