from decimal import Decimal

from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.constants import AMOUNT_NET_PERCENTAGE


def validate_update_contract_value(request):
    value = request.validated['data'].get('value')
    if value:
        for ro_attr in (
            'amount', 'amount_escp', 'amountPerformance', 'amountPerformance_npv',
            'yearlyPaymentsPercentage', 'annualCostsReduction', 'contractDuration',
            'currency', 'valueAddedTaxIncluded'
        ):
            if value.get(ro_attr) != request.context.value.to_native().get(ro_attr):
                raise_operation_error(request, 'Can\'t update {} for contract value'.format(ro_attr))

        award = [a for a in request.validated['tender'].awards if a.id == request.context.awardID][0]
        amount = value.get('amount')
        amount_net = value.get('amountNet')

        if amount_net is not None:
            if amount_net > award.value.amount:
                raise_operation_error(
                    request, 'Value amountNet should be less or equal to awarded amount ({})'.format(
                        award.value.amount))

            amount_max = amount_net + amount_net * Decimal(AMOUNT_NET_PERCENTAGE)
            if amount > amount_max:
                raise_operation_error(
                    request, 'Value amount can\'t be greater than amountNet ({}) for {}% ({})'.format(
                        amount_net, AMOUNT_NET_PERCENTAGE * 100, amount_max))
