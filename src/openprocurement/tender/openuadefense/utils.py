from logging import getLogger

from openprocurement.tender.core.utils import (
    calculate_clarif_business_date as calculate_clarif_business_date_base,
)
from openprocurement.tender.core.utils import (
    calculate_complaint_business_date as calculate_complaint_business_date_base,
)
from openprocurement.tender.core.utils import (
    calculate_tender_business_date as calculate_tender_business_date_base,
)
from openprocurement.tender.openuadefense.constants import WORKING_DAYS

LOGGER = getLogger("openprocurement.tender.openuadefense")


def calculate_tender_business_date(date_obj, timedelta_obj, tender=None, working_days=False):
    return calculate_tender_business_date_base(
        date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=WORKING_DAYS
    )


def calculate_complaint_business_date(date_obj, timedelta_obj, tender=None, working_days=False):
    return calculate_complaint_business_date_base(
        date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=WORKING_DAYS
    )


def calculate_clarif_business_date(date_obj, timedelta_obj, tender=None, working_days=False):
    return calculate_clarif_business_date_base(
        date_obj, timedelta_obj, tender=tender, working_days=working_days, calendar=WORKING_DAYS
    )
