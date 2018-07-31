import unittest
from openprocurement.agreement.cfaua.tests import create


def suite():
    suite = unittest.TestSuite()
    suite.addTest(create.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')