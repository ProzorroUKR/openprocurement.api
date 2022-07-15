from decimal import Decimal


# lots
class LotMinimalStepPercentageValues:
    MIN_VALUE = Decimal("0.005")
    MAX_VALUE = Decimal("0.03")
    PRECISION = -5


class LotYearlyPaymentsPercentageRangeValues:
    MIN_VALUE = Decimal("0")
    MAX_VALUE = Decimal("1")
    PRECISION = -5
