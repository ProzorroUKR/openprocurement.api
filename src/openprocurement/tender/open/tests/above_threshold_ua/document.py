import unittest

from openprocurement.tender.open.tests.below_threshold.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.open.tests.above_threshold_ua.base import BaseTenderUAContentWebTest


class TenderDocumentResourceTest(BaseTenderUAContentWebTest, TenderDocumentResourceTestMixin):
    should_add_contract_proforma_doc = False


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
