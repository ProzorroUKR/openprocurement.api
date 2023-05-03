from schematics.types import StringType
from schematics.validate import ValidationError
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriodEndRequired,
    StartedEnquiryPeriodEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
    PatchTender as BasePatchTender,
    Tender as BaseTender,
)
from openprocurement.tender.belowthreshold.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.validation import validate_tender_period_duration
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.api.models import ModelType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19
from datetime import timedelta


def validate_enquiry_period(data, period):
    if (
        get_first_revision_date(data, default=get_now()) > RELEASE_2020_04_19
        and period and period.startDate and period.endDate
        and period.endDate < calculate_tender_business_date(period.startDate, timedelta(days=3), data, True)
    ):
        raise ValidationError("the enquiryPeriod cannot end earlier than 3 business days after the start")


def validate_tender_period(data, period):
    if data.get("enquiryPeriod") and data.get("enquiryPeriod").endDate:
        if period.startDate:
            if period.startDate < data.get("enquiryPeriod").endDate:
                raise ValidationError("period should begin after enquiryPeriod")
        else:
            period.startDate = data.get("enquiryPeriod").endDate  # default tenderPeriod.startDate

    active_validation = get_first_revision_date(data, default=get_now()) > RELEASE_2020_04_19
    if (
            active_validation
            and period
            and period.startDate
            and period.endDate
    ):
        validate_tender_period_duration(data, period, timedelta(days=2), working_days=True)


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[BELOW_THRESHOLD], default=BELOW_THRESHOLD)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    enquiryPeriod = ModelType(StartedEnquiryPeriodEndRequired, required=True)

    def validate_enquiryPeriod(self, data, period):
        validate_enquiry_period(data, period)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period(data, period)


class PatchTender(BasePatchTender):
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired)
    procuringEntity = ModelType(ProcuringEntity)


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[BELOW_THRESHOLD], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired, required=True)

    def validate_enquiryPeriod(self, data, period):
        validate_enquiry_period(data, period)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period(data, period)
