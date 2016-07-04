# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from schematics.exceptions import ValidationError
from schematics.types import StringType
from openprocurement.api.models import ListType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.models import ITender, Period, get_now,TZ
from openprocurement.tender.openua.models import (
    Tender as BaseTender, EnquiryPeriod, Lot as BaseLot, get_tender, calc_auction_end_time, validate_lots_uniq,
)

from openprocurement.tender.openua.utils import calculate_business_date


STAND_STILL_TIME = timedelta(days=4)
ENQUIRY_STAND_STILL_TIME = timedelta(days=2)
CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_SUBMIT_TIME = timedelta(days=2)
COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
TENDER_PERIOD = timedelta(days=6)
ENQUIRY_PERIOD_TIME = timedelta(days=3)
TENDERING_EXTRA_PERIOD = timedelta(days=2)


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        if tender.status not in ['active.tendering', 'active.auction'] or lot.status != 'active':
            return
        if tender.status == 'active.auction' and lot.numberOfBids < 2:
            return
        if self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            return calc_auction_end_time(lot.numberOfBids, self.startDate).isoformat()
        else:
            decision_dates = [
                datetime.combine(complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo))
                for complaint in tender.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.tenderPeriod.endDate)
            return max(decision_dates).isoformat()

class Lot(BaseLot):

    auctionPeriod = ModelType(LotAuctionPeriod, default={})


@implementer(ITender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    procurementMethodType = StringType(default="aboveThresholdUA.defense")
    procuring_entity_kinds = ['defense']

    def initialize(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self, True)
        self.enquiryPeriod = EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                                endDate=endDate,
                                                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                                clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self, True)
        return EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                  endDate=endDate,
                                  invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                  clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    def validate_tenderPeriod(self, data, period):
        if period and calculate_business_date(period.startDate, TENDER_PERIOD, data, True) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {0.days} working days".format(TENDER_PERIOD))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        if self.tenderPeriod.startDate < COMPLAINT_OLD_SUBMIT_TIME_BEFORE:
            return Period(dict(startDate=self.tenderPeriod.startDate,
                               endDate=calculate_business_date(self.tenderPeriod.endDate, -COMPLAINT_OLD_SUBMIT_TIME, self)))
        else:
            return Period(dict(startDate=self.tenderPeriod.startDate,
                               endDate=calculate_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self, True)))
