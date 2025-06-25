from datetime import timedelta

BELOW_THRESHOLD = "belowThreshold"

MIN_BIDS_NUMBER = 2
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"],
}
TENDERING_EXTRA_PERIOD = timedelta(days=2)
