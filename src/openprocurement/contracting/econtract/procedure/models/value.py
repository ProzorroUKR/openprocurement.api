from decimal import Decimal

from openprocurement.api.models import ModelType, ListType, DecimalType, ContractValue as BaseContractValue
from openprocurement.tender.esco.procedure.models.value import ContractDuration


class ContractValue(BaseContractValue):
    # ESCO fields extends
    amountPerformance = DecimalType(
        required=False, precision=-2
    )
    yearlyPaymentsPercentage = DecimalType(precision=-5, min_value=Decimal("0"), max_value=Decimal("1"))
    annualCostsReduction = ListType(DecimalType())
    contractDuration = ModelType(ContractDuration)
