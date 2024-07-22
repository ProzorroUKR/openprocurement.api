import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.esco.tests.base import BaseESCOContentWebTest


class TenderDocumentResourceTest(BaseESCOContentWebTest, TenderDocumentResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
