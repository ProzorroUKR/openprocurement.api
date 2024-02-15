import unittest

from openprocurement.framework.core.tests import agreement, framework


def suite():
    suite = unittest.TestSuite()
    suite.addTest(framework.suite())
    suite.addTest(agreement.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
