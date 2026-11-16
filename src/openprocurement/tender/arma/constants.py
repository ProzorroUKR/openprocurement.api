from datetime import timedelta
from typing import Literal

from openprocurement.api.constants import ProcurementMethodType

ARMAProcurementMethodType = Literal[ProcurementMethodType.COMPLEX_ASSET_ARMA, ProcurementMethodType.SIMPLE_ASSET_ARMA]  # type: ignore[valid-type]


ARMA_ROUTE_PREFIX = "arma"

ARMA_CLAIM_SUBMIT_TIME = timedelta(days=10)
ARMA_TENDERING_EXTRA_PERIOD = timedelta(days=7)

ARMA_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
