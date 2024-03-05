import unittest
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.tests.base import BaseTenderWebTest
from openprocurement.tender.pricequotation.tests.criterion_blanks import (
    create_tender_criteria_multi_profile,
)


@patch(
    "openprocurement.tender.pricequotation.procedure.models.requirement.PQ_CRITERIA_ID_FROM",
    get_now() + timedelta(days=1),
)
class TenderPQCriteriaTest(BaseTenderWebTest):
    def setUp(self):
        super().setUp()
        self.create_agreement()

    test_create_tender_criteria_multi_profile = snitch(create_tender_criteria_multi_profile)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderPQCriteriaTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
