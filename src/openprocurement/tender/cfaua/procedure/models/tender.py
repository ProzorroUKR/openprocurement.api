from schematics.validate import ValidationError
from schematics.types import StringType, IntType, BaseType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType, ListType
from decimal import Decimal
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
    validate_cpv_group,
)
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PeriodStartEndRequired,
    StartedPeriodEndRequired,
    Period,
)
from openprocurement.tender.cfaua.constants import (
    CFA_UA,
    TENDERING_DURATION,
    QUESTIONS_STAND_STILL,
    ENQUIRY_STAND_STILL_TIME,
)
from openprocurement.tender.cfaua.validation import (
    validate_max_agreement_duration_period,
    validate_max_awards_number,
)
from openprocurement.tender.core.procedure.models.lot import (
    PostTenderLot,
    PatchTenderLot,
    Lot,
    validate_lots_uniq,
)
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.cfaua.procedure.models.feature import Feature
from openprocurement.tender.cfaua.procedure.models.organization import ProcuringEntity
from openprocurement.tender.cfaua.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
    PatchTender as BasePatchTender,
    Tender as BaseTender,
)
from openprocurement.tender.core.utils import (
    calculate_complaint_business_date,
    validate_features_custom_weight,
    calculate_tender_business_date,
    calculate_clarif_business_date,
)
from openprocurement.tender.core.models import validate_features_uniq
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.tender.openua.validation import _validate_tender_period_start_date
from openprocurement.tender.core.validation import validate_tender_period_duration
from openprocurement.api.validation import validate_items_uniq
from openprocurement.api.models import IsoDurationType


LOTS_MIN_SIZE = 1
LOTS_MAX_SIZE = 1


def validate_features(data, features):
    validate_related_items(data, features)
    if features:
        for i in features:
            if i.featureOf == "lot":
                raise ValidationError("Features are not allowed for lots")
    validate_features_custom_weight(data, features, Decimal("0.3"))


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[CFA_UA], default=CFA_UA)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    mainProcurementCategory = StringType(choices=["goods", "services"])

    agreementDuration = IsoDurationType(required=True, validators=[validate_max_agreement_duration_period])
    maxAwardsCount = IntType(required=True, validators=[validate_max_awards_number])

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    lots = ListType(ModelType(PostTenderLot, required=True), required=True,
                    min_size=LOTS_MIN_SIZE, max_size=LOTS_MAX_SIZE, validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])

    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)

    status = StringType(choices=["draft"], default="draft")

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    def validate_tenderPeriod(self, data, period):
        if period:
            _validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_features(data, features)

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


class PatchTender(BasePatchTender):
    procurementMethodType = StringType(choices=[CFA_UA])
    procuringEntity = ModelType(ProcuringEntity)
    mainProcurementCategory = StringType(choices=["goods", "services"])
    agreementDuration = IsoDurationType(validators=[validate_max_agreement_duration_period])
    maxAwardsCount = IntType(validators=[validate_max_awards_number])

    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    lots = ListType(ModelType(PatchTenderLot, required=True),
                    min_size=LOTS_MIN_SIZE, max_size=LOTS_MAX_SIZE, validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])

    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired)

    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification.stand-still",
            "active.qualification",
            "active.qualification.stand-still",
        ],
    )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[CFA_UA], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    mainProcurementCategory = StringType(choices=["goods", "services"])
    agreementDuration = IsoDurationType(required=True, validators=[validate_max_agreement_duration_period])
    maxAwardsCount = IntType(required=True, validators=[validate_max_awards_number])

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    lots = ListType(ModelType(Lot, required=True), required=True,
                    min_size=LOTS_MIN_SIZE, max_size=LOTS_MAX_SIZE, validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])

    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)

    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.qualification",
            "active.qualification.stand-still",
        ],
    )

    auctionPeriod = ModelType(Period)
    qualificationPeriod = ModelType(Period)
    qualifications = BaseType()
    awards = BaseType()

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    def validate_tenderPeriod(self, data, period):
        validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_features(data, features)

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
