from openprocurement.api.utils import raise_operation_error


def validate_update_contract_value(request):
    value = request.validated['data'].get('value')
    if value:
        for ro_attr in (
            'amount', 'amount_escp', 'amountPerformance', 'amountPerformance_npv',
            'yearlyPaymentsPercentage', 'annualCostsReduction', 'contractDuration',
            'currency'
        ):
            if value.get(ro_attr) != request.context.value.to_native().get(ro_attr):
                raise_operation_error(request, 'Can\'t update {} for contract value'.format(ro_attr))
