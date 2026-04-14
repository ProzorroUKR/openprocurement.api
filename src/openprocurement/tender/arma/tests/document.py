import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_lots,
)
from openprocurement.tender.arma.tests.document_blanks import (
    create_acceptance_report_document_pre_qualification,
)
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))


class TenderDraftDocumentResourceTest(TenderDocumentResourceTest):
    initial_status = "draft"
    initial_auth = ("Basic", ("broker", ""))


class TenderPreQualificationDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification"
    initial_bids = test_tender_arma_bids
    initial_lots = test_tender_arma_lots
    initial_auth = ("Basic", ("broker", ""))

    test_create_acceptance_report_document = snitch(create_acceptance_report_document_pre_qualification)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDraftDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderPreQualificationDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
