import unittest

from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetContentWebTest,
)
from openprocurement.tender.open.tests.below_threshold.document import (
    TenderDocumentResourceTestMixin,
)


class TenderDocumentResourceTest(BaseTenderSimpleAssetContentWebTest, TenderDocumentResourceTestMixin):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    should_add_contract_proforma_doc = False


class TenderDraftDocumentResourceTest(TenderDocumentResourceTest):
    initial_status = "draft"
    initial_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDraftDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
