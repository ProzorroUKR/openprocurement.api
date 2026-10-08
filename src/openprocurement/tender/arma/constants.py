from datetime import timedelta

COMPLEX_ASSET_ARMA: str = "complexAsset.arma"
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
