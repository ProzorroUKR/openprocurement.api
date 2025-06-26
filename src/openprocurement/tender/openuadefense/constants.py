from datetime import datetime, timedelta

import standards

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.models.organization import ProcuringEntityKind

WORKING_DAYS = {}
HOLIDAYS = standards.load("calendars/workdays_off.json")
WORKING_WEEKENDS = standards.load("calendars/weekends_on.json")
for date_str in HOLIDAYS:
    WORKING_DAYS[date_str] = True
for date_str in WORKING_WEEKENDS:
    WORKING_DAYS[date_str] = False

CLAIM_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME = timedelta(days=3)
COMPLAINT_OLD_SUBMIT_TIME_BEFORE = datetime(2016, 7, 5, tzinfo=TZ)
TENDERING_EXTRA_PERIOD = timedelta(days=2)
ABOVE_THRESHOLD_UA_DEFENSE = "aboveThresholdUA.defense"

DEFENSE_PROCURING_ENTITY_KIND_CHOICES = (
    ProcuringEntityKind.AUTHORITY.value,
    ProcuringEntityKind.CENTRAL.value,
    ProcuringEntityKind.DEFENSE.value,
    ProcuringEntityKind.GENERAL.value,
    ProcuringEntityKind.SOCIAL.value,
    ProcuringEntityKind.SPECIAL.value,
)

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": True,
    "qualificationComplainDuration": False,
}
