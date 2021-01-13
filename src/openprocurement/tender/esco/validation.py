from openprocurement.tender.core.validation import validate_update_contract_value


def validate_update_contract_value_esco(request, **kwargs):
    validate_update_contract_value(
        request,
        attrs=(
            "amount",
            "amount_escp",
            "amountPerformance",
            "amountPerformance_npv",
            "yearlyPaymentsPercentage",
            "annualCostsReduction",
            "contractDuration",
            "currency",
        ),
    )
