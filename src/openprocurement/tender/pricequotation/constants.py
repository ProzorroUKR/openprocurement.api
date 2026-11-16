from datetime import timedelta
from typing import Literal

from openprocurement.api.constants import (
    PQ_PROFILE_PATTERN,  # noqa: F401
    ProcurementMethodType,
)

PriceQuotationProcurementMethodType = Literal[ProcurementMethodType.PRICE_QUOTATION]  # type: ignore[valid-type]


PQ_QUALIFICATION_DURATION = timedelta(days=2)

PQ_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
