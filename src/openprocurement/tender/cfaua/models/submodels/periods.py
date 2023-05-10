from datetime import datetime, timedelta, time

from schematics.types import StringType

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
            raise ValidationError("period should begin before its end")


class TenderAuctionPeriod(Period):
    shouldStartAfter = StringType()


class ContractPeriod(Period):
    clarificationsUntil = IsoDateTimeType()


class LotAuctionPeriod(Period):
    shouldStartAfter = StringType()
