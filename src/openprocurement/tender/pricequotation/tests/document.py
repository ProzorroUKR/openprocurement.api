import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentWithDSResourceTestMixin,
)
from openprocurement.tender.pricequotation.tests.base import TenderContentWebTest
from openprocurement.tender.pricequotation.tests.document_blanks import (
    create_document_active_tendering_status,
)


class TenderDocumentWithDSResourceTest(TenderContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
