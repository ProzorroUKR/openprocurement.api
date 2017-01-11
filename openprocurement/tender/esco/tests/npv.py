import unittest
from openprocurement.tender.esco.utils import calculate_npv

nbu_rate = 0.22


class NPVCalculationTest(unittest.TestCase):
    """ NPV Calculation Test
        based on data from https://docs.google.com/spreadsheets/d/1kOz6bxob4Nmb0Es_W0TmbNznoYDcnwAKcSgxfPEXYGQ/edit#gid=1469973930
    """

    def test_case1(self):
        annualCostsReduction = 751.5
        yearlyPayments = 0.9
        contractDuration = 10
        npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                                yearlyPayments, contractDuration)
        self.assertEqual(npv_val, 698.444)

    def test_case2(self):
        annualCostsReduction = 300.6
        yearlyPayments = 0.9
        contractDuration = 6
        npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                                yearlyPayments, contractDuration)
        self.assertEqual(npv_val, 483.978)

    def test_case3(self):
        annualCostsReduction = 225.45
        yearlyPayments = 0.9
        contractDuration = 4
        npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                                yearlyPayments, contractDuration)
        self.assertEqual(npv_val, 499.595)

    def test_case4(self):
        annualCostsReduction = 75.15
        yearlyPayments = 0.9
        contractDuration = 2
        npv_val = calculate_npv(nbu_rate, annualCostsReduction,
                                yearlyPayments, contractDuration)
        self.assertEqual(npv_val, 234.309)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NPVCalculationTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
