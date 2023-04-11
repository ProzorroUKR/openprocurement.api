import unittest

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.open.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.belowthreshold.tests.document import TenderDocumentWithDSResourceTestMixin


class TenderDocumentWithDSResourceTest(BaseTenderUAContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    initial_lots = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
