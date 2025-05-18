from datetime import datetime, timedelta

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.models.organization import ProcuringEntityKind

TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
TENDERING_AUCTION = timedelta(days=35)
QUESTIONS_STAND_STILL = timedelta(days=10)
BID_UNSUCCESSFUL_FROM = datetime(2016, 10, 18, tzinfo=TZ)
ABOVE_THRESHOLD_EU = "aboveThresholdEU"

EU_PROCURING_ENTITY_KIND_CHOICES = (
    ProcuringEntityKind.AUTHORITY.value,
    ProcuringEntityKind.CENTRAL.value,
    ProcuringEntityKind.DEFENSE.value,
    ProcuringEntityKind.GENERAL.value,
    ProcuringEntityKind.SOCIAL.value,
    ProcuringEntityKind.SPECIAL.value,
)
