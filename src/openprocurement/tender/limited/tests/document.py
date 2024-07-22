import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
    test_tender_reporting_data,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    initial_data = test_tender_reporting_data


class TenderNegotiationDocumentResourceTest(TenderDocumentResourceTest):
    initial_data = test_tender_negotiation_data
    initial_config = test_tender_negotiation_config


class TenderNegotiationQuickDocumentResourceTest(TenderNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderNegotiationDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderNegotiationQuickDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
