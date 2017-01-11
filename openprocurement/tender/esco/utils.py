from openprocurement.tender.esco.constants import NPV_CALCULATION_DURATION


def calculate_npv(nbu_rate, annualCostsReduction, yearlyPayments,
                  contractDuration):
    CRfree = annualCostsReduction
    CR = CRfree - annualCostsReduction * yearlyPayments
    value = sum([(CR if i <= contractDuration else CRfree)/(1 + nbu_rate)**i
                 for i in range(1, NPV_CALCULATION_DURATION + 1)])
    return round(value, 3)
