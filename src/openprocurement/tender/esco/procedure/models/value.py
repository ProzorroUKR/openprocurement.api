from datetime import datetime
from decimal import Decimal

from esculator import escp, npv
from schematics.exceptions import ValidationError
from schematics.types import BooleanType, IntType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import DecimalType, ListType, StringDecimalType
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.esco.procedure.utils import to_decimal


class ContractDuration(Model):
    years = IntType(required=True, min_value=0, max_value=15)
    days = IntType(required=False, min_value=0, max_value=364, default=0)

    def validate_days(self, data, days):
        if data["years"] == 15 and days > 0:
            raise ValidationError("max contract duration 15 years")
        if data["years"] == 0 and days < 1:
            raise ValidationError("min contract duration 1 day")


class BasicESCOValue(BasicValue):
    # Calculated energy service contract value.
    amount = DecimalType(min_value=Decimal("0"), required=False, precision=-2)


class ESCOValue(BasicESCOValue):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)
    # Calculated energy service contract performance indicator
    amountPerformance = DecimalType(required=False, precision=-2)
    # The percentage of annual payments in favor of Bidder
    yearlyPaymentsPercentage = DecimalType(precision=-5, min_value=Decimal("0"), max_value=Decimal("1"))
    # Buyer's annual costs reduction
    annualCostsReduction = ListType(StringDecimalType())
    # Contract duration
    contractDuration = ModelType(ContractDuration)


class PatchESCOValue(ESCOValue):
    def validate_annualCostsReduction(self, data, value):
        if value is not None and len(value) != 21:
            raise ValidationError("annual costs reduction should be set for 21 period")


class ESCODynamicValue(ESCOValue):
    # The percentage of annual payments in favor of Bidder
    yearlyPaymentsPercentage = DecimalType(required=True, precision=-5, min_value=Decimal("0"), max_value=Decimal("1"))
    # Buyer's annual costs reduction
    annualCostsReduction = ListType(StringDecimalType(), required=True)
    # Contract duration
    contractDuration = ModelType(ContractDuration, required=True)

    @serializable(serialized_name="amountPerformance", type=DecimalType(precision=-2))
    def amountPerformance_npv(self):
        """Calculated energy service contract performance indicator"""
        tender = get_tender()
        return to_decimal(
            npv(
                self.contractDuration.years,
                self.contractDuration.days,
                self.yearlyPaymentsPercentage,
                self.annualCostsReduction,
                dt_from_iso(tender["noticePublicationDate"]),
                tender["NBUdiscountRate"],
            )
        )

    @serializable(serialized_name="amount", type=DecimalType(precision=-2))
    def amount_escp(self):
        tender = get_tender()
        return to_decimal(
            escp(
                self.contractDuration.years,
                self.contractDuration.days,
                self.yearlyPaymentsPercentage,
                self.annualCostsReduction,
                datetime.fromisoformat(tender["noticePublicationDate"]),
            )
        )

    def validate_annualCostsReduction(self, data, value):
        if len(value) != 21:
            raise ValidationError("annual costs reduction should be set for 21 period")

    def validate_yearlyPaymentsPercentage(self, data, value):
        tender = get_tender()

        if tender["fundingKind"] == "other":
            min_value = 0.8
            if value < Decimal(str(min_value)):
                raise ValidationError(
                    "yearlyPaymentsPercentage should be greater than {} and less than 1".format(min_value)
                )

        if tender.get("lots"):
            # Validation for lots is done in the state
            # (maybe this one further should be moved to the state as well)
            return

        if tender["fundingKind"] == "budget":
            max_value = tender["yearlyPaymentsPercentageRange"]
            if value > Decimal(str(max_value)):
                raise ValidationError(
                    "yearlyPaymentsPercentage should be greater than 0 and less than {}".format(max_value)
                )


class ESCOWeightedValue(BasicESCOValue):
    # Calculated energy service contract performance indicator
    amountPerformance = DecimalType(required=False, precision=-2)

    denominator = DecimalType()
    addition = DecimalType(precision=-2)

    # Keep for backward compatibility
    valueAddedTaxIncluded = BooleanType()


class ContractESCOValue(ESCOValue):
    amountNet = DecimalType(min_value=Decimal("0"), precision=-2)
