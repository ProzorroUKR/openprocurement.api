# -*- coding: utf-8 -*-
from datetime import timedelta

STAND_STILL_TIME = timedelta(days=2)
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"],
}
BOT_NAME = "fa_bot"
DRAFT_FIELDS = ("shortlistedFirms",)

ENQUIRY_PERIOD = timedelta(days=1)
TENDERING_DURATION = timedelta(days=3)
AUCTION_DURATION = timedelta(days=1)  # needs to be updated
COMPLAINT_DURATION = timedelta(days=1)  # needs to be updated
CLARIFICATIONS_DURATION = timedelta(days=5)  # needs to be updated
TENDER_PERIOD_MINIMAL_DURATION = timedelta(days=3)
MIN_PERIOD_UNTIL_AGREEMENT_END = timedelta(days=7)
MIN_ACTIVE_CONTRACTS = 3
MINIMAL_STEP_PERCENTAGE = 0.005

CFA_SELECTION = "closeFrameworkAgreementSelectionUA"
CFA_SELECTION_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")
