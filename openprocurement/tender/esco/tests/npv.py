import unittest
from openprocurement.tender.esco.tests.base import snitch

from openprocurement.tender.esco.tests.npv_blanks import (
    npv_case1, npv_case2, npv_case3, npv_case4
)


class NPVCalculationTest(unittest.TestCase):
    """ NPV Calculation Test
        based on data from https://docs.google.com/spreadsheets/d/1kOz6bxob4Nmb0Es_W0TmbNznoYDcnwAKcSgxfPEXYGQ/edit#gid=1469973930
    """

    test_case1 = snitch(npv_case1)
    test_case2 = snitch(npv_case2)
    test_case3 = snitch(npv_case3)
    test_case4 = snitch(npv_case4)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NPVCalculationTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
