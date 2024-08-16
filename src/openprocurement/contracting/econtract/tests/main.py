import unittest

from openprocurement.contracting.econtract.tests import contract, document


def suite():
    suite = unittest.TestSuite()
    suite.addTest(contract.suite())
    suite.addTest(document.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
