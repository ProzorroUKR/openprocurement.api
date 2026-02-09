import unittest

from openprocurement.tender.arma.tests.base import BaseTenderContentWebTest
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
