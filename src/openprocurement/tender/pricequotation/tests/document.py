import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
)
from openprocurement.tender.pricequotation.tests.base import TenderContentWebTest
from openprocurement.tender.pricequotation.tests.document_blanks import (
    create_document_active_tendering_status,
)


class TenderDocumentResourceTest(TenderContentWebTest, TenderDocumentResourceTestMixin):

    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
