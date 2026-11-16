from enum import StrEnum
from uuid import uuid4

from pydantic import Field, field_validator, model_validator

from openprocurement.api.constants import (
    FUNDER_PROGRAM_SCHEME,
    FUNDER_PROGRAMS,
    KPK,
    PLAN_OF_UKRAINE,
    PLAN_OF_UKRAINE_SCHEME,
    TKPKMB,
    TKPKMB_SCHEME,
)
from openprocurement.api.constants_env import BUDGET_PERIOD_FROM
from openprocurement.api.enums import enum_members
from openprocurement.api.procedure.errors import REQUIRED_MESSAGE, FieldError, FieldErrors
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model, model_field_validator, validate_uniq_id
from openprocurement.api.procedure.models.item import Classification
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import MD5, IsoDateTime
from openprocurement.api.procedure.utils import is_const_active
from openprocurement.planning.api.constants import BreakdownTitle

_BUDGET_PROJECT_CLASSIFIERS: dict[str, tuple[dict, str]] = {
    FUNDER_PROGRAM_SCHEME: (FUNDER_PROGRAMS, "name_uk"),
    PLAN_OF_UKRAINE_SCHEME: (PLAN_OF_UKRAINE, "name_uk"),
}


class BudgetProjectScheme(StrEnum):
    FUNDER_PROGRAM = FUNDER_PROGRAM_SCHEME
    PLAN_OF_UKRAINE = PLAN_OF_UKRAINE_SCHEME


BudgetClassificationScheme = StrEnum(  # type: ignore[misc]
    "BudgetClassificationScheme", enum_members([*KPK.keys(), TKPKMB_SCHEME])
)


class BudgetProject(Model):
    id: str
    name: str
    name_en: str | None = None
    name_ru: str | None = None
    scheme: BudgetProjectScheme | None = None

    def _classifier_entry(self) -> tuple[str | None, dict | None, str | None]:
        scheme = self.scheme

        if scheme is None and self.id in PLAN_OF_UKRAINE:
            scheme = PLAN_OF_UKRAINE_SCHEME

        if scheme not in _BUDGET_PROJECT_CLASSIFIERS:
            return None, None, None

        classifier, name_key = _BUDGET_PROJECT_CLASSIFIERS[scheme]

        return scheme, classifier.get(self.id), name_key

    @model_validator(mode="after")
    def validate_id(self):
        if not self.scheme:
            # scheme is mandatory once the id refers to a known program dictionary,
            # so that a donor programme can't be smuggled in without its scheme.
            if self.id in FUNDER_PROGRAMS or self.id in PLAN_OF_UKRAINE:
                raise FieldError("id", "scheme is required for a known budget project id")
            return self
        entry = _BUDGET_PROJECT_CLASSIFIERS[self.scheme][0].get(self.id)
        if entry is None:
            raise FieldError("id", f"{self.scheme} id not found in standards")
        if entry.get("archive"):
            raise FieldError("id", f"{self.scheme} program is archived")
        return self

    @model_validator(mode="after")
    def validate_names(self):
        scheme, entry, name_key = self._classifier_entry()
        if entry:
            message = f"Value should be from {scheme} dictionary for {self.id}"
            errors = {}
            if self.name != entry[name_key]:
                errors["name"] = message
            if self.name_en != entry["name_en"]:
                errors["name_en"] = message
            if errors:
                raise FieldErrors(errors)
        return self


class BudgetPeriod(Period):
    startDate: IsoDateTime
    endDate: IsoDateTime


class BudgetClassification(Classification):
    scheme: BudgetClassificationScheme

    @model_field_validator("id")
    def validate_id(self, value):
        if self.scheme in KPK and value not in KPK[self.scheme]:
            raise ValueError(f"{self.scheme} id not found in standards")
        if self.scheme == TKPKMB_SCHEME and value not in TKPKMB:
            raise ValueError(f"{TKPKMB_SCHEME} id not found in standards")


class BudgetBreakdownItem(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    title: BreakdownTitle
    description: str | None = Field(None, max_length=500)
    description_en: str | None = Field(None, max_length=500)
    description_ru: str | None = Field(None, max_length=500)
    value: BasicValue
    address: Address | None = None
    classification: BudgetClassification | None = None

    @model_validator(mode="after")
    def validate_description(self):
        if self.title == BreakdownTitle.OTHER and not self.description:
            raise FieldError("description", REQUIRED_MESSAGE)
        return self


class Budget(Model):
    id: str
    description: str
    description_en: str | None = None
    description_ru: str | None = None
    amount: float
    currency: str = Field("UAH", max_length=3, min_length=3)  # The currency in 3-letter ISO 4217 format.
    amountNet: float | None = None
    project: BudgetProject | None = None
    period: BudgetPeriod | None = None
    year: int | None = Field(None, ge=2000)
    notes: str | None = None
    breakdown: list[BudgetBreakdownItem] | None = None

    @field_validator("period")
    @classmethod
    def validate_period(cls, period: BudgetPeriod) -> BudgetPeriod:
        if period and not is_const_active(BUDGET_PERIOD_FROM):
            raise ValueError("Can't use period field, use year field instead")
        return period

    @field_validator("year")
    @classmethod
    def validate_year(cls, year: int) -> int:
        if year and is_const_active(BUDGET_PERIOD_FROM):
            raise ValueError("Can't use year field, use period field instead")
        return year

    @field_validator("breakdown")
    @classmethod
    def validate_breakdown_items(cls, breakdown: list[BudgetBreakdownItem]) -> list:
        validate_uniq_id(breakdown)
        return breakdown

    @model_field_validator("breakdown")
    def validate_breakdown(self, breakdown):
        if breakdown:
            currencies = {item.value.currency for item in breakdown} | {self.currency}
            if len(currencies) > 1:
                raise ValueError("Currency should be identical for all budget breakdown values and budget")
