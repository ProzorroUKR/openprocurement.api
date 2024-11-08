from datetime import timedelta

REQUEST_FOR_PROPOSAL = "requestForProposal"
TENDERING_DAYS = 4
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
STAND_STILL_TIME = timedelta(days=2)
ENQUIRY_STAND_STILL_TIME = timedelta(days=1)

MIN_BIDS_NUMBER = 2
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"],
}
TENDERING_EXTRA_PERIOD = timedelta(days=4)
