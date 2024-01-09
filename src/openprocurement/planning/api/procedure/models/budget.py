from uuid import uuid4

from openprocurement.planning.api.constants import (
    BREAKDOWN_TITLES,
    BREAKDOWN_OTHER,
)
from schematics.exceptions import ValidationError
from schematics.types import StringType, FloatType, IntType, BaseType, MD5Type
from schematics.types.compound import ModelType

from openprocurement.api.constants import BUDGET_PERIOD_FROM, LOGGER
from openprocurement.api.procedure.utils import is_const_active
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, IsoDateTimeType
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.item import validate_items_uniq
from openprocurement.planning.api.procedure.models.guarantee import Guarantee


class Project(Model):
    id = StringType(required=True)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()


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
    project = ModelType(Project)
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
