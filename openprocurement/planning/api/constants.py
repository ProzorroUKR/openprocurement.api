from datetime import datetime

from openprocurement.api.constants import TZ

PROCEDURES = {
    '': (
        '',
    ),
    'open': (
        'belowThreshold',
        'aboveThresholdUA',
        'aboveThresholdEU',
        'aboveThresholdUA.defense',
        'competitiveDialogueUA',
        'competitiveDialogueEU',
        'esco',
        'closeFrameworkAgreementUA',
    ),
    'limited': (
        'reporting',
        'negotiation',
        'negotiation.quick',
    ),
}

MULTI_YEAR_BUDGET_PROCEDURES = (
    'closeFrameworkAgreementUA',
)

BUDGET_PERIOD_FROM = datetime(2018, 10, 1, tzinfo=TZ)