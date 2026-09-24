import unittest

from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.open.tests.below_threshold.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.open.tests.competitive_ordering.long.base import (
    BaseTenderCOLongContentWebTest,
)


class TenderDocumentResourceTest(BaseTenderCOLongContentWebTest, TenderDocumentResourceTestMixin):
    initial_lots = test_tender_below_lots
    should_add_contract_proforma_doc = False


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
