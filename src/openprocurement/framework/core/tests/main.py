import unittest

from openprocurement.framework.core.tests import framework


def suite():
    suite = unittest.TestSuite()
    suite.addTest(framework.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
