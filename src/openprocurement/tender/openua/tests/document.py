import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest


class TenderDocumentResourceTest(BaseTenderUAContentWebTest, TenderDocumentResourceTestMixin):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
