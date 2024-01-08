from datetime import datetime

from isodate import duration_isoformat
from schematics.validate import ValidationError
from schematics.types import StringType, IntType, BaseType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType, ListType
from decimal import Decimal
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
)
from openprocurement.api.procedure.models.item import validate_cpv_group
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PeriodStartEndRequired,
    StartedPeriodEndRequired,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.tender.cfaua.constants import (
    CFA_UA,
    TENDERING_DURATION,
    MIN_BIDS_NUMBER,
    MAX_AGREEMENT_PERIOD,
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
)
from openprocurement.tender.core.procedure.utils import validate_features_custom_weight
from openprocurement.tender.openua.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_start_date,
    validate_tender_period_duration,
)
from openprocurement.api.procedure.validation import validate_features_uniq
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


def validate_max_awards_number(number, *args):
    if number < MIN_BIDS_NUMBER:
        raise ValidationError("Maximal awards number can't be less then minimal bids number")


def validate_max_agreement_duration_period(value):
    date = datetime(1, 1, 1)
    if (date + value) > (date + MAX_AGREEMENT_PERIOD):
        raise ValidationError(
            "Agreement duration period is greater than {}".format(duration_isoformat(MAX_AGREEMENT_PERIOD))
        )



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
        validators=[validate_items_uniq, validate_classification_id],
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
            validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_features(data, features)


class PatchTender(BasePatchTender):
    procurementMethodType = StringType(choices=[CFA_UA])
    procuringEntity = ModelType(ProcuringEntity)
    mainProcurementCategory = StringType(choices=["goods", "services"])
    agreementDuration = IsoDurationType(validators=[validate_max_agreement_duration_period])
    maxAwardsCount = IntType(validators=[validate_max_awards_number])

    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
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
        validators=[validate_items_uniq, validate_classification_id],
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
            "active.auction",
            "active.qualification",
            "active.qualification.stand-still",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
    )

    auctionPeriod = ModelType(Period)
    awards = BaseType()

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    def validate_tenderPeriod(self, data, period):
        validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_features(data, features)