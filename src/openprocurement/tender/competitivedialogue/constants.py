# constants for procurementMethodtype
CD_UA_TYPE = "competitiveDialogueUA"
CD_EU_TYPE = "competitiveDialogueEU"
STAGE_2_EU_TYPE = "competitiveDialogueEU.stage2"
STAGE_2_UA_TYPE = "competitiveDialogueUA.stage2"

STAGE2_STATUS = "draft.stage2"

FEATURES_MAX_SUM = 0.99
MINIMAL_NUMBER_OF_BIDS = 3

STAGE_2_EU_DEFAULT_CONFIG = {
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
    "restricted": False,
}
STAGE_2_UA_DEFAULT_CONFIG = {
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
    "restricted": False,
}
