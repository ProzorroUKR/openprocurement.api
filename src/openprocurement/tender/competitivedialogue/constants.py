from datetime import timedelta

# constants for procurementMethodtype
CD_UA_TYPE = "competitiveDialogueUA"
CD_EU_TYPE = "competitiveDialogueEU"
STAGE_2_EU_TYPE = "competitiveDialogueEU.stage2"
STAGE_2_UA_TYPE = "competitiveDialogueUA.stage2"

CD_STAGE2_STATUS = "draft.stage2"

CD_FEATURES_MAX_SUM = 0.99
CD_MINIMAL_NUMBER_OF_BIDS = 3

CD_STAGE_2_EU_DEFAULT_CONFIG = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": True,
    "minBidsNumber": 2,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": True,
    "hasQualificationComplaints": True,
    "tenderComplainRegulation": 4,
    "qualificationComplainDuration": 5,
    "awardComplainDuration": 10,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 3,
    "qualificationDuration": 20,
    "minTenderingDuration": 30,
    "hasEnquiries": False,
    "minEnquiriesDuration": 0,
    "enquiryPeriodRegulation": 10,
    "restricted": False,
    "hasMultiSourcing": False,
}
CD_STAGE_2_UA_DEFAULT_CONFIG = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 2,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 4,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 10,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 3,
    "qualificationDuration": 0,
    "minTenderingDuration": 15,
    "hasEnquiries": False,
    "minEnquiriesDuration": 0,
    "enquiryPeriodRegulation": 10,
    "restricted": False,
    "hasMultiSourcing": False,
}

CD_STAGE_1_EU_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

CD_STAGE_1_UA_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

CD_STAGE_2_EU_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}

CD_STAGE_2_UA_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": False,
    "minEnquiriesDuration": False,
    "enquiryPeriodRegulation": False,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}
CD_CLAIM_SUBMIT_TIME = timedelta(days=10)
CD_TENDERING_EXTRA_PERIOD = timedelta(days=7)
