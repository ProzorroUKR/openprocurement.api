import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest,
    test_tender_data,
)
from openprocurement.tender.pricequotation.tests.criterion_blanks import (
    create_tender_criteria_multi_profile
)


class TenderPQCriteriaTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_criteria_multi_profile = snitch(create_tender_criteria_multi_profile)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderPQCriteriaTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")