from datetime import timedelta

STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"],
}
BOT_NAME = "fa_bot"
DRAFT_FIELDS = ("shortlistedFirms",)

AUCTION_DURATION = timedelta(days=1)  # needs to be updated
COMPLAINT_DURATION = timedelta(days=1)  # needs to be updated
TENDER_PERIOD_MINIMAL_DURATION = timedelta(days=3)
MIN_PERIOD_UNTIL_AGREEMENT_END = timedelta(days=7)
MIN_ACTIVE_CONTRACTS = 3
MINIMAL_STEP_PERCENTAGE = 0.005

CFA_SELECTION = "closeFrameworkAgreementSelectionUA"
CFA_SELECTION_KINDS = (
    "authority",
    "central",
    "defense",
    "general",
    "other",
    "social",
    "special",
)

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
