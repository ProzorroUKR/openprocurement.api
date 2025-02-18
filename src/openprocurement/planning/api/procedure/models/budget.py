from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, FloatType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import BUDGET_PERIOD_FROM, PLAN_OF_UKRAINE
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import validate_items_uniq
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.procedure.utils import is_const_active
from openprocurement.planning.api.constants import (
    BREAKDOWN_OTHER,
    BREAKDOWN_TITLES,
    UKRAINE_FACILITY_PROJECT,
)
from openprocurement.planning.api.procedure.models.guarantee import Guarantee


class BudgetProject(Model):
    id = StringType(required=True)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()

    def validate_name(self, data, value):
        if data.get("id") == UKRAINE_FACILITY_PROJECT and value not in PLAN_OF_UKRAINE:
            raise ValidationError(f"Value should be one of plan_of_ukraine dictionary for {data['id']}")

    def validate_id(self, data, value):
        if data.get("name") in PLAN_OF_UKRAINE and value != UKRAINE_FACILITY_PROJECT:
            raise ValidationError(f"Value should be '{UKRAINE_FACILITY_PROJECT}' for name {data['name']}")


class BudgetPeriod(Period):
    startDate = IsoDateTimeType(required=True)
    endDate = IsoDateTimeType(required=True)


class BudgetBreakdownItem(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, choices=BREAKDOWN_TITLES)
    description = StringType(max_length=500)
    description_en = StringType(max_length=500)
    description_ru = StringType(max_length=500)
    value = ModelType(Guarantee, required=True)

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
    breakdown = ListType(ModelType(BudgetBreakdownItem, required=True), validators=[validate_items_uniq])

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
