import unittest

from openprocurement.tender.core.tests import models, tender, tender_credentials, utils


def suite():
    suite = unittest.TestSuite()
    suite.addTest(tender.suite())
    suite.addTest(models.suite())
    suite.addTest(utils.suite())
    suite.addTest(tender_credentials.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
