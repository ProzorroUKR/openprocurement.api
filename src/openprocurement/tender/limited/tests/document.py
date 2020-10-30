# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
    TenderDocumentWithDSResourceTestMixin,
)

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    initial_data = test_tender_data
    docservice = False


class TenderNegotiationDocumentResourceTest(TenderDocumentResourceTest):
    initial_data = test_tender_negotiation_data


class TenderNegotiationQuickDocumentResourceTest(TenderNegotiationDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_tender_contract_proforma_document_json = None
    test_create_tender_contract_proforma_document_json_invalid = None
    test_create_tender_documents_by_registry_bot = None
    test_create_tender_documents_by_registry_bot_invalid = None
    test_create_tender_contract_data_document_json = None
    test_upload_tender_document_by_renderer_bot = None
    test_patch_tender_contract_proforma_document_invalid = None
    test_put_tender_contract_proforma_document = None
    test_upload_tender_document_contract_proforma_by_rbot_fail = None


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
