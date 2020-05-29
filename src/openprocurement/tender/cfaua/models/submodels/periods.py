from datetime import datetime, timedelta, time

from openprocurement.api.models import IsoDateTimeType
from openprocurement.api.utils import get_now
from openprocurement.tender.cfaua.constants import TENDERING_AUCTION
from openprocurement.tender.core.models import get_tender
from openprocurement.api.models import PeriodEndRequired as BasePeriodEndRequired, Period
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    normalize_should_start_after,
    calculate_tender_date,
)
from schematics.exceptions import ValidationError
from schematics.types.serializable import serializable


class PeriodEndRequired(BasePeriodEndRequired):
    # TODO different validator compared with belowthreshold
    def validate_startDate(self, data, value):
        if value and data.get("endDate") and data.get("endDate") < value:
            raise ValidationError(u"period should begin before its end")


class TenderAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = self.__parent__
        if tender.lots or tender.status not in [
            "active.tendering",
            "active.pre-qualification.stand-still",
            "active.auction",
        ]:
            return
        start_after = None
        if tender.status == "active.tendering" and tender.tenderPeriod.endDate:
            start_after = calculate_tender_date(tender.tenderPeriod.endDate, TENDERING_AUCTION, tender)
        elif self.startDate and get_now() > calc_auction_end_time(tender.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(tender.numberOfBids, self.startDate)
        elif tender.qualificationPeriod and tender.qualificationPeriod.endDate:
            decision_dates = [
                datetime.combine(
                    complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo)
                )
                for qualification in tender.qualifications
                for complaint in qualification.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.qualificationPeriod.endDate)
            start_after = max(decision_dates)
        if start_after:
            return normalize_should_start_after(start_after, tender).isoformat()


class ContractPeriod(Period):
    clarificationsUntil = IsoDateTimeType()


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        statuses = ["active.tendering", "active.pre-qualification.stand-still", "active.auction"]
        if tender.status not in statuses or lot.status != "active":
            return
        start_after = None
        if tender.status == "active.tendering" and tender.tenderPeriod.endDate:
            start_after = calculate_tender_date(tender.tenderPeriod.endDate, TENDERING_AUCTION, tender)
        elif self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(lot.numberOfBids, self.startDate)
        elif tender.qualificationPeriod and tender.qualificationPeriod.endDate:
            decision_dates = [
                datetime.combine(
                    complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo)
                )
                for qualification in tender.qualifications
                for complaint in qualification.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.qualificationPeriod.endDate)
            start_after = max(decision_dates)
        if start_after:
            return normalize_should_start_after(start_after, tender).isoformat()
