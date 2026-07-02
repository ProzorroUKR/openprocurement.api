from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, FloatType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType

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
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import Classification
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.procedure.utils import is_const_active
from openprocurement.api.validation import validate_uniq_id
from openprocurement.planning.api.constants import BREAKDOWN_OTHER, BREAKDOWN_TITLES

_BUDGET_PROJECT_CLASSIFIERS: dict[str, tuple[dict, str]] = {
    FUNDER_PROGRAM_SCHEME: (FUNDER_PROGRAMS, "name"),
    PLAN_OF_UKRAINE_SCHEME: (PLAN_OF_UKRAINE, "name_uk"),
}
BUDGET_PROJECT_SCHEMES: tuple[str, ...] = tuple(_BUDGET_PROJECT_CLASSIFIERS)


def _budget_project_classifier_entry(
    data: dict,
) -> tuple[str | None, dict | None, str | None]:
    scheme = data.get("scheme")

    if scheme is None and data.get("id") in PLAN_OF_UKRAINE:
        scheme = PLAN_OF_UKRAINE_SCHEME

    if scheme not in _BUDGET_PROJECT_CLASSIFIERS:
        return None, None, None

    classifier, name_key = _BUDGET_PROJECT_CLASSIFIERS[scheme]

    return scheme, classifier.get(data.get("id")), name_key


class BudgetProject(Model):
    id = StringType(required=True)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    scheme = StringType(choices=BUDGET_PROJECT_SCHEMES)

    def validate_id(self, data: dict, value: str) -> None:
        scheme = data.get("scheme")
        if not scheme:
            # scheme is mandatory once the id refers to a known program dictionary,
            # so that a donor programme can't be smuggled in without its scheme.
            if value in FUNDER_PROGRAMS or value in PLAN_OF_UKRAINE:
                raise ValidationError("scheme is required for a known budget project id")
            return
        entry = _BUDGET_PROJECT_CLASSIFIERS[scheme][0].get(value)
        if entry is None:
            raise ValidationError(f"{scheme} id not found in standards")
        if entry.get("archive"):
            raise ValidationError(f"{scheme} program is archived")

    def validate_name(self, data: dict, value: str) -> None:
        scheme, entry, name_key = _budget_project_classifier_entry(data)
        if entry and value != entry[name_key]:
            raise ValidationError(f"Value should be from {scheme} dictionary for {data['id']}")

    def validate_name_en(self, data: dict, value: str) -> None:
        scheme, entry, _ = _budget_project_classifier_entry(data)
        if entry and value != entry["name_en"]:
            raise ValidationError(f"Value should be from {scheme} dictionary for {data['id']}")


class BudgetPeriod(Period):
    startDate = IsoDateTimeType(required=True)
    endDate = IsoDateTimeType(required=True)


class BudgetClassification(Classification):
    scheme = StringType(
        required=True,
        choices=[
            *KPK.keys(),
            TKPKMB_SCHEME,
        ],
    )

    def validate_id(self, data, value):
        for kpk_scheme, kpk_dict in KPK.items():
            if data["scheme"] == kpk_scheme and value not in kpk_dict:
                raise ValidationError(f"{kpk_scheme} id not found in standards")
        if data["scheme"] == TKPKMB_SCHEME and value not in TKPKMB:
            raise ValidationError(f"{TKPKMB_SCHEME} id not found in standards")


class BudgetBreakdownItem(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, choices=BREAKDOWN_TITLES)
    description = StringType(max_length=500)
    description_en = StringType(max_length=500)
    description_ru = StringType(max_length=500)
    value = ModelType(BasicValue, required=True)
    address = ModelType(Address)
    classification = ModelType(BudgetClassification)

    def validate_description(self, data, value):
        if data.get("title", None) == BREAKDOWN_OTHER and not value:
            raise ValidationError(BaseType.MESSAGES["required"])


class Budget(Model):
    id = StringType(required=True)
    description = StringType(required=True)
    description_en = StringType()
    description_ru = StringType()
    amount = FloatType(required=True)
    currency = StringType(
        required=False, default="UAH", max_length=3, min_length=3
    )  # The currency in 3-letter ISO 4217 format.
    amountNet = FloatType()
    project = ModelType(BudgetProject)
    period = ModelType(BudgetPeriod)
    year = IntType(min_value=2000)
    notes = StringType()
    breakdown = ListType(ModelType(BudgetBreakdownItem, required=True), validators=[validate_uniq_id])

    def validate_period(self, budget, period):
        if period and not is_const_active(BUDGET_PERIOD_FROM):
            raise ValidationError("Can't use period field, use year field instead")

    def validate_year(self, budget, year):
        if year and is_const_active(BUDGET_PERIOD_FROM):
            raise ValidationError("Can't use year field, use period field instead")

    def validate_breakdown(self, budget, breakdown):
        if breakdown:
            currencies = [i["value"]["currency"] for i in breakdown]
            if "currency" in budget:
                currencies.append(budget["currency"])
            if len(set(currencies)) > 1:
                raise ValidationError("Currency should be identical for all budget breakdown values and budget")
