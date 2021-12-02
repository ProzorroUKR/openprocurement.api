import unittest
from unittest.mock import patch
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.pricequotation.tests.base import TenderContentWebTest
from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
    TenderDocumentWithDSResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.document_blanks import\
    create_tender_document_error
from openprocurement.tender.pricequotation.tests.document_blanks import (
    create_document_active_tendering_status,
)


@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() + timedelta(days=1))
class TenderDocumentResourceTest(TenderContentWebTest, TenderDocumentResourceTestMixin):
    """"""
    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)


@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() + timedelta(days=1))
class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_tender_document_error = snitch(create_tender_document_error)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
