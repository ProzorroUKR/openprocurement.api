# -*- coding: utf-8 -*-
from datetime import timedelta
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.models import ITender, Period
from openprocurement.tender.openua.models import Tender as BaseTender
from openprocurement.tender.openua.utils import calculate_business_date

STAND_STILL_TIME = timedelta(days=2)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
CLAIM_SUBMIT_TIME = timedelta(days=2)
COMPLAINT_SUBMIT_TIME = timedelta(days=2)
TENDER_PERIOD = timedelta(days=5)
ENQUIRY_PERIOD_TIME = timedelta(days=2)
TENDERING_EXTRA_PERIOD = timedelta(days=2)


@implementer(ITender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    procurementMethodType = StringType(default="aboveThresholdUA.defense")

    def validate_tenderPeriod(self, data, period):
        if period and calculate_business_date(period.startDate, TENDER_PERIOD) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than 5 days")

    @serializable(serialized_name="enquiryPeriod", type=ModelType(Period))
    def tender_enquiryPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME)))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME)))
