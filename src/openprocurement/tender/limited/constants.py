from openprocurement.api.procedure.models.organization import ProcuringEntityKind

REPORTING = "reporting"
NEGOTIATION = "negotiation"
NEGOTIATION_QUICK = "negotiation.quick"

LIMITED_WORKING_DAYS_CONFIG = {
    "minTenderingDuration": True,
    "minEnquiriesDuration": True,
    "enquiryPeriodRegulation": True,
    "clarificationUntilDuration": True,
    "tenderComplainRegulation": False,
    "qualificationComplainDuration": False,
}


LIMITED_COMMON_VALUE_AMOUNT_THRESHOLD = {
    "goods": 200000,
    "services": 200000,
    "works": 1500000,
}

LIMITED_VALUE_AMOUNT_THRESHOLD_MAPPING = {
    ProcuringEntityKind.AUTHORITY: LIMITED_COMMON_VALUE_AMOUNT_THRESHOLD,
    ProcuringEntityKind.DEFENSE: LIMITED_COMMON_VALUE_AMOUNT_THRESHOLD,
    ProcuringEntityKind.GENERAL: LIMITED_COMMON_VALUE_AMOUNT_THRESHOLD,
    ProcuringEntityKind.SOCIAL: LIMITED_COMMON_VALUE_AMOUNT_THRESHOLD,
    ProcuringEntityKind.SPECIAL: {
        "goods": 1000000,
        "services": 1000000,
        "works": 5000000,
    },
}

# negotiation causes
basic_cause_choices = [
    "twiceUnsuccessful",
    "additionalPurchase",
    "additionalConstruction",
    "stateLegalServices",
]

cause_choices = [
    "artContestIP",
    "noCompetition",
] + basic_cause_choices

cause_choices_new = [
    "resolvingInsolvency",
    "artPurchase",
    "contestWinner",
    "technicalReasons",
    "intProperty",
    "lastHope",
] + basic_cause_choices

cause_choices_quick = cause_choices + ["quick"]
cause_choices_quick_new = cause_choices_new + [
    "emergency",
    "humanitarianAid",
    "contractCancelled",
    "activeComplaint",
]
