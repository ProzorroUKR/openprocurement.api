from datetime import timedelta
from typing import Literal

from openprocurement.api.constants import ProcurementMethodType

ESCOProcurementMethodType = Literal[ProcurementMethodType.ESCO]  # type: ignore[valid-type]


ESCO_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
ESCO_TENDERING_EXTRA_PERIOD = timedelta(days=7)
