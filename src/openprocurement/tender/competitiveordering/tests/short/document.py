import unittest

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.competitiveordering.tests.short.base import (
    BaseTenderCOShortContentWebTest,
)


class TenderDocumentResourceTest(BaseTenderCOShortContentWebTest, TenderDocumentResourceTestMixin):
    initial_lots = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
