from decimal import Decimal

from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import DecimalType, ListType
from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.core.constants import AWARD_CRITERIA_CHOICES
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.period import EnquiryPeriod
from openprocurement.tender.core.procedure.models.tender import (
    PatchTenderFeaturesMixin,
    PatchTenderItemsMixin,
    PatchTenderMilestonesMixin,
    PostTenderItemsMixin,
    PostTenderPeriodsMixin,
    TenderFeaturesMixin,
    TenderGuaranteeMixin,
    TenderItemsMixin,
    TenderMilestonesMixin,
    TenderPeriodsMixin,
    TenderSubmissionMixin,
    validate_esco_lots_yearly_payments_percentage_range,
    validate_esco_yearly_payments_percentage_range,
)
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PatchBaseTender, PostBaseTender
from openprocurement.tender.core.procedure.models.value import PostEstimatedValue
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.esco.procedure.models.lot import ESCOLot, ESCOPatchTenderLot, ESCOPostTenderLot


class ESCOPostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderPeriodsMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procurementMethodType = StringType(choices=[ESCO], default=ESCO)
    minValue = ModelType(PostEstimatedValue, default={"currency": "UAH", "valueAddedTaxIncluded": False})
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    yearlyPaymentsPercentageRange = DecimalType(
        min_value=Decimal("0"),
        max_value=Decimal("1"),
        precision=-5,
    )
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")

    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(ESCOPostTenderLot, required=True), validators=[validate_uniq_id])

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        validate_esco_yearly_payments_percentage_range(data, value)

    def validate_lots(self, data, lots):
        validate_esco_lots_yearly_payments_percentage_range(data, lots)


class ESCOPatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderItemsMixin,
    PatchTenderFeaturesMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procurementMethodType = StringType(choices=[ESCO])
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    yearlyPaymentsPercentageRange = DecimalType(min_value=Decimal("0"), max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"])

    procuringEntity = ModelType(ProcuringEntity)
    lots = ListType(ModelType(ESCOPatchTenderLot, required=True), validators=[validate_uniq_id])


class ESCOTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    TenderPeriodsMixin,
    TenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    BaseTender,
):
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES, required=True)
    procurementMethodType = StringType(choices=[ESCO], required=True)
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    minValue = ModelType(PostEstimatedValue)
    yearlyPaymentsPercentageRange = DecimalType(min_value=Decimal("0"), max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"], required=True)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(ESCOLot, required=True), validators=[validate_uniq_id])

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        validate_esco_yearly_payments_percentage_range(data, value)

    def validate_lots(self, data, lots):
        validate_esco_lots_yearly_payments_percentage_range(data, lots)
