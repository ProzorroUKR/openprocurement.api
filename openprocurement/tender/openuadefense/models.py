# -*- coding: utf-8 -*-
from datetime import timedelta
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.models import ITender, Period
from openprocurement.tender.openua.models import Tender as BaseTender, EnquiryPeriod
from openprocurement.tender.openua.utils import calculate_business_date

STAND_STILL_TIME = timedelta(days=2)
ENQUIRY_STAND_STILL_TIME = timedelta(days=3)
CLAIM_SUBMIT_TIME = timedelta(days=2)
COMPLAINT_SUBMIT_TIME = timedelta(days=2)
TENDER_PERIOD = timedelta(days=5)
ENQUIRY_PERIOD_TIME = timedelta(days=2)
TENDERING_EXTRA_PERIOD = timedelta(days=2)


@implementer(ITender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    procurementMethodType = StringType(default="aboveThresholdUA.defense")
    procuring_entity_kinds = ['defense']

    def initialize(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self, True)
        self.enquiryPeriod = EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                                endDate=endDate,
                                                clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self, True)
        return EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                  endDate=endDate,
                                  clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    def validate_tenderPeriod(self, data, period):
        if period and calculate_business_date(period.startDate, TENDER_PERIOD, data, True) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {0.days} working days".format(TENDER_PERIOD))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate,
                           endDate=calculate_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)))
