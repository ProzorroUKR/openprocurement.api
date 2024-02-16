import unittest

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentWithDSResourceTestMixin,
)
from openprocurement.tender.open.tests.base import BaseTenderUAContentWebTest


class TenderDocumentWithDSResourceTest(BaseTenderUAContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    initial_lots = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
