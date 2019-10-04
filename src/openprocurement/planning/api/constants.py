PROCEDURES = {
    "": ("", "centralizedProcurement"),
    "open": (
        "belowThreshold",
        "aboveThresholdUA",
        "aboveThresholdEU",
        "aboveThresholdUA.defense",
        "competitiveDialogueUA",
        "competitiveDialogueEU",
        "esco",
        "closeFrameworkAgreementUA",
    ),
    "limited": ("reporting", "negotiation", "negotiation.quick"),
}

MULTI_YEAR_BUDGET_PROCEDURES = ("closeFrameworkAgreementUA",)
MULTI_YEAR_BUDGET_MAX_YEARS = 4

BREAKDOWN_OTHER = "other"
BREAKDOWN_TITLES = ["state", "crimea", "local", "own", "fund", "loan", BREAKDOWN_OTHER]
