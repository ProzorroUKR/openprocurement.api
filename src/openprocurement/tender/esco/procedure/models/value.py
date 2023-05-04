from decimal import Decimal
from schematics.types import IntType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from datetime import datetime
from esculator import npv, escp
from openprocurement.api.models import (
    Value,
    Model,
    ListType,
)
from openprocurement.tender.core.procedure.models.base import DecimalType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.esco.utils import to_decimal


class ContractDuration(Model):
    years = IntType(required=True, min_value=0, max_value=15)
    days = IntType(required=False, min_value=0, max_value=364, default=0)

    def validate_days(self, data, days):
        if data["years"] == 15 and days > 0:
            raise ValidationError("max contract duration 15 years")
        if data["years"] == 0 and days < 1:
            raise ValidationError("min contract duration 1 day")


class BaseESCOValue(Value):
    amount = DecimalType(
        min_value=Decimal("0"), required=False, precision=-2
    )  # Calculated energy service contract value.
    amountPerformance = DecimalType(
        required=False, precision=-2
    )  # Calculated energy service contract performance indicator
    yearlyPaymentsPercentage = DecimalType(precision=-5, min_value=Decimal("0"), max_value=Decimal("1"))
    # The percentage of annual payments in favor of Bidder
    annualCostsReduction = ListType(DecimalType())  # Buyer's annual costs reduction
    contractDuration = ModelType(ContractDuration)
    denominator = DecimalType()
    addition = DecimalType()


class PatchESCOValue(BaseESCOValue):

    def validate_annualCostsReduction(self, data, value):
        if value is not None and len(value) != 21:
            raise ValidationError("annual costs reduction should be set for 21 period")


class ESCOValue(BaseESCOValue):
    amount = DecimalType(
        min_value=Decimal("0"), required=False, precision=-2
    )  # Calculated energy service contract value.
    amountPerformance = DecimalType(
        required=False, precision=-2
    )  # Calculated energy service contract performance indicator
    yearlyPaymentsPercentage = DecimalType(
        required=True, precision=-5, min_value=Decimal("0"), max_value=Decimal("1")
    )  # The percentage of annual payments in favor of Bidder
    annualCostsReduction = ListType(DecimalType(), required=True)  # Buyer's annual costs reduction
    contractDuration = ModelType(ContractDuration, required=True)

    @serializable(serialized_name="amountPerformance", type=DecimalType(precision=-2))
    def amountPerformance_npv(self):
        """ Calculated energy service contract performance indicator """
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
        if data.get("status") != "draft":
            parent = data["__parent__"]
            tender = get_tender()

            if tender["fundingKind"] == "other" and value < Decimal("0.8"):
                raise ValidationError("yearlyPaymentsPercentage should be greater than 0.8 and less than 1")
            if tender["fundingKind"] == "budget":
                if tender.get("lots"):
                    lots = [i for i in tender.get("lots", "") if i["id"] == parent["relatedLot"]]

                    if lots and value > Decimal(lots[0]["yearlyPaymentsPercentageRange"]):
                        raise ValidationError(
                            "yearlyPaymentsPercentage should be greater than 0 and less than {}".format(
                                lots[0]["yearlyPaymentsPercentageRange"]
                            )
                        )
                else:
                    if value > Decimal(tender["yearlyPaymentsPercentageRange"]):
                        raise ValidationError(
                            "yearlyPaymentsPercentage should be greater than 0 and less than {}".format(
                                tender["yearlyPaymentsPercentageRange"]
                            )
                        )


class ContractESCOValue(BaseESCOValue):
    amountNet = DecimalType(min_value=Decimal("0"), precision=-2)
