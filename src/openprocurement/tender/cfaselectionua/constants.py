from datetime import timedelta
from typing import Literal

from openprocurement.api.constants import ProcurementMethodType

CFA_SELECTION_STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "tender_owner": ["claim"],
}
CFA_SELECTION_BOT_NAME = "fa_bot"
CFA_SELECTION_DRAFT_FIELDS = ("shortlistedFirms",)

CFA_SELECTION_AUCTION_DURATION = timedelta(days=1)  # needs to be updated
CFA_SELECTION_COMPLAINT_DURATION = timedelta(days=1)  # needs to be updated
CFA_SELECTION_TENDER_PERIOD_MINIMAL_DURATION = timedelta(days=3)
CFA_SELECTION_MIN_PERIOD_UNTIL_AGREEMENT_END = timedelta(days=7)
CFA_SELECTION_MIN_ACTIVE_CONTRACTS = 3
CFA_SELECTION_MINIMAL_STEP_PERCENTAGE = 0.005


CFASelectionUAProcurementMethodType = Literal[ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA]  # type: ignore[valid-type]


CFA_SELECTION_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
