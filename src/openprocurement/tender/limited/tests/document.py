# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentWithDSResourceTestMixin,
)

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_reporting_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentWithDSResourceTestMixin):
    initial_data = test_tender_reporting_data
    docservice = True


class TenderNegotiationDocumentResourceTest(TenderDocumentResourceTest):
    initial_data = test_tender_negotiation_data


class TenderNegotiationQuickDocumentResourceTest(TenderNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True


class TenderNegotiationDocumentWithDSResourceTest(TenderDocumentWithDSResourceTest):
    initial_data = test_tender_negotiation_data


class TenderNegotiationQuickDocumentWithDSResourceTest(TenderDocumentWithDSResourceTest):
    initial_data = test_tender_negotiation_quick_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
