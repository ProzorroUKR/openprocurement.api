# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, time
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.utils import get_now
from openprocurement.api.models import (
    Period,
    ListType,
    ContactPoint as BaseContactPoint
)
from openprocurement.tender.core.models import (
    ProcuringEntity as BaseProcuringEntity, EnquiryPeriod,
    Lot as BaseLot, validate_lots_uniq, get_tender
)
from openprocurement.tender.openua.models import (
    Tender as BaseTender,
    IAboveThresholdUATender,
)
from openprocurement.tender.openua.utils import calculate_normalized_date
from openprocurement.tender.core.utils import (
    calculate_business_date,
    calc_auction_end_time,
)
from openprocurement.tender.openuadefense.constants import (
    TENDER_PERIOD,
    ENQUIRY_STAND_STILL_TIME,
    ENQUIRY_PERIOD_TIME,
    COMPLAINT_SUBMIT_TIME,
    COMPLAINT_OLD_SUBMIT_TIME,
    COMPLAINT_OLD_SUBMIT_TIME_BEFORE
)


class IAboveThresholdUADefTender(IAboveThresholdUATender):
     """ Marker interface for aboveThresholdUA defense tenders """


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


class ContactPoint(BaseContactPoint):

    availableLanguage = StringType(choices=['uk', 'en', 'ru'])


class ProcuringEntity(BaseProcuringEntity):

    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True),
                                       required=False)


@implementer(IAboveThresholdUADefTender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    procurementMethodType = StringType(default="aboveThresholdUA.defense")
    procuring_entity_kinds = ['defense']

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
            normalized_end = calculate_normalized_date(self.tenderPeriod.endDate, self)
            return Period(dict(startDate=self.tenderPeriod.startDate,
                               endDate=calculate_business_date(normalized_end, -COMPLAINT_SUBMIT_TIME, self, True)))
