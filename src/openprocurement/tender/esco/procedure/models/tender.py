from decimal import Decimal
from schematics.validate import ValidationError
from schematics.types import StringType, BaseType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType, ListType
from openprocurement.api.models import DecimalType, Value, Model, IsoDateTimeType
from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.procedure.models.period import (
    PeriodEndRequired,
    StartedPeriodEndRequired,
    EnquiryPeriod,
    Period,
    TenderAuctionPeriod,
)
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.esco.procedure.models.feature import Feature
from openprocurement.tender.core.procedure.models.milestone import Milestone, validate_milestones_lot
from openprocurement.tender.core.procedure.models.guarantee import Guarantee, PostGuarantee
from openprocurement.tender.core.procedure.models.item import (
    validate_cpv_group,
    validate_items_uniq,
    validate_classification_id,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.lot import validate_lots_uniq
from openprocurement.tender.esco.procedure.models.lot import PostLot, PatchLot, Lot
from openprocurement.tender.core.procedure.models.tender import validate_milestones, validate_items_related_lot
from openprocurement.tender.core.procedure.models.tender_base import (
    PostBaseTender,
    PatchBaseTender,
    BaseTender,
)
from openprocurement.tender.esco.procedure.models.item import Item
from openprocurement.tender.esco.constants import (
    ESCO,
    TENDERING_DURATION,
    QUESTIONS_STAND_STILL,
    ENQUIRY_STAND_STILL_TIME,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_RATED_CRITERIA
from openprocurement.tender.core.models import validate_features_uniq
from openprocurement.tender.core.validation import validate_tender_period_duration
from openprocurement.tender.core.utils import (
    validate_features_custom_weight,
    calculate_tender_business_date,
    calculate_clarif_business_date,
)
from openprocurement.tender.openeu.procedure.models.organization import ProcuringEntity
from openprocurement.tender.openua.validation import _validate_tender_period_start_date


class ESCOSerializable(Model):
    @serializable(serialized_name="minValue", type=ModelType(Value))
    def tender_minValue(self):
        return (
            Value(
                dict(
                    amount=sum([i.minValue.amount for i in self.lots]),
                    currency=self.minValue.currency,
                    valueAddedTaxIncluded=self.minValue.valueAddedTaxIncluded,
                )
            )
            if self.lots
            else self.minValue
        )

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {"amount": sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee["currency"] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee["currency"] = self.guarantee.currency
            return Guarantee(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStepPercentage")
    def tender_minimalStepPercentage(self):
        return min([i.minimalStepPercentage for i in self.lots]) if self.lots else self.minimalStepPercentage

    @serializable(serialized_name="yearlyPaymentsPercentageRange")
    def tender_yearlyPaymentsPercentageRange(self):
        return (
            min([i.yearlyPaymentsPercentageRange for i in self.lots])
            if self.lots
            else self.yearlyPaymentsPercentageRange
        )

    # @serializable(
    #     serialized_name="enquiryPeriod",
    #     serialize_when_none=True,
    #     type=ModelType(EnquiryPeriod, required=False)
    # )
    # def tender_enquiryPeriod(self):
    #     enquiry_period_class = self._fields["enquiryPeriod"]
    #     end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
    #     clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, self, True)
    #     return enquiry_period_class(
    #         dict(
    #             startDate=self.tenderPeriod.startDate,
    #             endDate=end_date,
    #             invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
    #             clarificationsUntil=clarifications_until,
    #         )
    #     )


def validate_yearly_payments_percentage_range(data, value):
    if data["fundingKind"] == "other" and value != Decimal("0.8"):
        raise ValidationError("when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8")
    if data["fundingKind"] == "budget" and (value > Decimal("0.8") or value < Decimal("0")):
        raise ValidationError(
            "when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
        )


def validate_award_period(data, period):
    if (
        period
        and period.startDate
        and data.get("auctionPeriod")
        and data.get("auctionPeriod").endDate
        and period.startDate < data.get("auctionPeriod").endDate
    ):
        raise ValidationError("period should begin after auctionPeriod")
    if (
        period
        and period.startDate
        and data.get("tenderPeriod")
        and data.get("tenderPeriod").endDate
        and period.startDate < data.get("tenderPeriod").endDate
    ):
        raise ValidationError("period should begin after tenderPeriod")


def validate_lots_yearly_payments_percentage_range(data, lots):
    if lots:
        if data["fundingKind"] == "other":
            for lot in lots:
                if lot["yearlyPaymentsPercentageRange"] != Decimal("0.8"):
                    raise ValidationError("when tender fundingKind is other, "
                                          "yearlyPaymentsPercentageRange should be equal 0.8")
        elif data["fundingKind"] == "budget":
            for lot in lots:
                value = lot["yearlyPaymentsPercentageRange"]
                if value > Decimal("0.8") or value < Decimal("0"):
                    raise ValidationError(
                        "when tender fundingKind is budget, "
                        "yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
                    )


class PostTender(ESCOSerializable, PostBaseTender):
    procurementMethod = StringType(choices=["open"], default="open")
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    submissionMethod = StringType(choices=["electronicAuction"], default="electronicAuction")
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethodType = StringType(choices=[ESCO], default=ESCO)
    status = StringType(choices=["draft"], default="draft")
    minValue = ModelType(Value, default={"amount": 0, "currency": "UAH", "valueAddedTaxIncluded": True})
    minimalStepPercentage = DecimalType(required=True, min_value=Decimal("0.005"),
                                        max_value=Decimal("0.03"), precision=-5)
    yearlyPaymentsPercentageRange = DecimalType(required=True, default=Decimal("0.8"),
                                                min_value=Decimal("0"), max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")
    guarantee = ModelType(PostGuarantee)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(PostLot, required=True), validators=[validate_lots_uniq])
    items = ListType(ModelType(Item, required=True), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)
    enquiryPeriod = ModelType(EnquiryPeriod)
    auctionPeriod = ModelType(TenderAuctionPeriod)
    awardPeriod = ModelType(Period)
    noticePublicationDate = IsoDateTimeType()

    def validate_tenderPeriod(self, data, period):
        if period:
            _validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        validate_yearly_payments_percentage_range(data, value)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, 0.25)

    def validate_lots(self, data, lots):
        validate_lots_yearly_payments_percentage_range(data, lots)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    @serializable(serialized_name="noticePublicationDate", serialize_when_none=False, type=IsoDateTimeType())
    def tender_noticePublicationDate(self):
        if self.status == "active.tendering":
            return get_now()


class PatchTender(PatchBaseTender):
    procurementMethod = StringType(choices=["open"])
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA])
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethodType = StringType(choices=[ESCO])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification.stand-still",
        ],
    )
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    yearlyPaymentsPercentageRange = DecimalType(min_value=Decimal("0"), max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"])
    guarantee = ModelType(Guarantee)

    procuringEntity = ModelType(ProcuringEntity)
    lots = ListType(ModelType(PatchLot, required=True), validators=[validate_lots_uniq])
    items = ListType(ModelType(Item, required=True), min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])
    tenderPeriod = ModelType(PeriodEndRequired)
    enquiryPeriod = ModelType(EnquiryPeriod)


class Tender(ESCOSerializable, BaseTender):
    procurementMethod = StringType(choices=["open"], required=True)
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], required=True)
    submissionMethod = StringType(choices=["electronicAuction"], required=True)
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethodType = StringType(choices=[ESCO], required=True)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification.stand-still",
            "active.pre-qualification",
        ],
        required=True
    )
    minimalStepPercentage = DecimalType(required=True, min_value=Decimal("0.005"),
                                        max_value=Decimal("0.03"), precision=-5)
    minValue = ModelType(Value, required=True)
    yearlyPaymentsPercentageRange = DecimalType(required=True, min_value=Decimal("0"),
                                                max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"], required=True)
    noticePublicationDate = IsoDateTimeType()
    guarantee = ModelType(Guarantee)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(Lot, required=True), validators=[validate_lots_uniq])
    items = ListType(ModelType(Item, required=True), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq, validate_classification_id])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    enquiryPeriod = ModelType(EnquiryPeriod)

    qualificationPeriod = BaseType()
    qualifications = BaseType()
    complaintPeriod = BaseType()
    auctionPeriod = ModelType(TenderAuctionPeriod)
    awardPeriod = ModelType(Period)
    next_check = BaseType()

    def validate_tenderPeriod(self, data, period):
        if period:
            # _validate_tender_period_start_date(data, period)  # ENABLED FOR POST ONLY
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        validate_yearly_payments_percentage_range(data, value)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, 0.25)

    def validate_lots(self, data, lots):
        validate_lots_yearly_payments_percentage_range(data, lots)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    @serializable(serialized_name="noticePublicationDate", serialize_when_none=False, type=IsoDateTimeType())
    def tender_noticePublicationDate(self):
        if not self.noticePublicationDate and self.status == "active.tendering":
            return get_now()
        else:
            return self.noticePublicationDate