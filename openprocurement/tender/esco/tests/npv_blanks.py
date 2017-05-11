from openprocurement.tender.esco.utils import calculate_npv


nbu_rate = 0.22


def case1(self):
    annualCostsReduction = 751.5
    yearlyPayments = 0.9
    contractDuration = 10
    npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                            yearlyPayments, contractDuration)
    self.assertEqual(npv_val, 698.444)


def case2(self):
    annualCostsReduction = 300.6
    yearlyPayments = 0.9
    contractDuration = 6
    npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                            yearlyPayments, contractDuration)
    self.assertEqual(npv_val, 483.978)


def case3(self):
    annualCostsReduction = 225.45
    yearlyPayments = 0.9
    contractDuration = 4
    npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                            yearlyPayments, contractDuration)
    self.assertEqual(npv_val, 499.595)


def case4(self):
    annualCostsReduction = 75.15
    yearlyPayments = 0.9
    contractDuration = 2
    npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                            yearlyPayments, contractDuration)
    self.assertEqual(npv_val, 234.309)
