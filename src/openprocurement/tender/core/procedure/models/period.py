from openprocurement.tender.core.utils import calc_auction_end_time, normalize_should_start_after
from openprocurement.api.models import IsoDateTimeType, Model
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.constants import CANT_DELETE_PERIOD_START_DATE_FROM
from openprocurement.tender.core.procedure.context import get_tender, get_now
from schematics.validate import ValidationError
from schematics.types.serializable import serializable
from datetime import datetime, timedelta, time


class Period(Model):
    startDate = IsoDateTimeType()  # The state date for the period.
    endDate = IsoDateTimeType()  # The end date for the period.

    def validate_startDate(self, data, value):
        if value and data.get("endDate") and data.get("endDate") < value:
            raise ValidationError("period should begin before its end")


class EnquiryPeriod(Period):
    clarificationsUntil = IsoDateTimeType()
    invalidationDate = IsoDateTimeType()


class PeriodEndRequired(Period):
    endDate = IsoDateTimeType(required=True)

    # def validate_startDate(self, data, period):
    #     super().validate_startDate(self, data, period)
    #
    #     date = get_first_revision_date(get_tender(), default=None)
    #     if date and date > CANT_DELETE_PERIOD_START_DATE_FROM and not period:
    #         raise ValidationError(["This field cannot be deleted"])


class PostPeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True, default=get_now)  # The state date for the period.
    endDate = IsoDateTimeType(required=True, default=get_now)  # The end date for the period.


class PeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True)  # The state date for the period.
    endDate = IsoDateTimeType(required=True)  # The end date for the period.


class StartedPeriodEndRequired(PeriodEndRequired):
    startDate = IsoDateTimeType(default=lambda: get_now().isoformat())


class LotAuctionPeriod(Period):
    shouldStartAfter = IsoDateTimeType()


class TenderAuctionPeriod(Period):
    shouldStartAfter = IsoDateTimeType()
