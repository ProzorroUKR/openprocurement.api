import unittest

from openprocurement.planning.api.tests import document, plan


def suite():
    suite = unittest.TestSuite()
    suite.addTest(plan.suite())
    suite.addTest(document.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
