import unittest
from openprocurement.framework.cfaua.tests import agreement, contract, document, change


def suite():
    suite = unittest.TestSuite()
    suite.addTest(agreement.suite())
    suite.addTest(document.suite())
    suite.addTest(contract.suite())
    suite.addTest(change.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
