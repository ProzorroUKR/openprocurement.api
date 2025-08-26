from datetime import timedelta

REQUEST_FOR_PROPOSAL = "requestForProposal"

MIN_BIDS_NUMBER = 2
STATUS4ROLE = {
    "complaint_owner": ["draft", "answered"],
    "reviewers": ["pending"],
    "tender_owner": ["claim"],
}
TENDERING_EXTRA_PERIOD = timedelta(days=4)

WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": False,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": True,
}
