# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
    TenderDocumentWithDSResourceTestMixin,
    create_lot_contract_proforma_document_json,
    create_lot_contract_proforma_document_json_invalid,
    create_lot_documents_by_registry_bot,
    create_lot_documents_by_registry_bot_invalid,
    create_lot_contract_data_document_json,
    upload_lot_document_by_renderer_bot,
)

from openprocurement.tender.cfaua.tests.base import BaseTenderContentWebTest


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    docservice = False
    initial_auth = ("Basic", ("broker", ""))


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_tender_contract_proforma_document_json = snitch(create_lot_contract_proforma_document_json)
    test_create_tender_contract_proforma_document_json_invalid = snitch(create_lot_contract_proforma_document_json_invalid)
    test_create_tender_documents_by_registry_bot = snitch(create_lot_documents_by_registry_bot)
    test_create_tender_documents_by_registry_bot_invalid = snitch(create_lot_documents_by_registry_bot_invalid)
    test_create_tender_contract_data_document_json = snitch(create_lot_contract_data_document_json)
    test_upload_tender_document_by_renderer_bot = snitch(upload_lot_document_by_renderer_bot)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
