import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.cfaua.tests.base import BaseTenderContentWebTest


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
