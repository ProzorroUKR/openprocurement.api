import unittest
from openprocurement.agreement.core.tests import agreement


def suite():
    suite = unittest.TestSuite()
    suite.addTest(agreement.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')