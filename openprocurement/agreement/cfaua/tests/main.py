import unittest
from openprocurement.agreement.cfaua.tests import (
    agreement,
    contract,
    document
)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(agreement.suite())
    suite.addTest(document.suite())
    suite.addTest(contract.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
