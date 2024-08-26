from logging import getLogger

from openprocurement.tender.core.utils import accelerated_tender
from openprocurement.tender.core.utils import (
    calculate_tender_full_date as calculate_tender_full_date_base,
)
from openprocurement.tender.openuadefense.constants import WORKING_DAYS

LOGGER = getLogger("openprocurement.tender.openuadefense")


@accelerated_tender
def calculate_tender_full_date(date_obj, timedelta_obj, working_days=False):
    return calculate_tender_full_date_base(date_obj, timedelta_obj, working_days=working_days, calendar=WORKING_DAYS)
