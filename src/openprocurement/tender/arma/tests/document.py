import unittest

from openprocurement.tender.arma.tests.base import BaseTenderContentWebTest
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))


class TenderDraftDocumentResourceTest(TenderDocumentResourceTest):
    initial_status = "draft"
    initial_auth = ("Basic", ("broker", ""))


class TenderPreQualificationDocumentResourceTest(TenderDocumentResourceTest):
    initial_status = "active.pre-qualification"
    initial_auth = ("Basic", ("broker", ""))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDraftDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderPreQualificationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
