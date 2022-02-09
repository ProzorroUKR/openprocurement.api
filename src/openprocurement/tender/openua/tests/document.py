import unittest
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.belowthreshold.tests.document import TenderDocumentWithDSResourceTestMixin


class TenderDocumentWithDSResourceTest(BaseTenderUAContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
