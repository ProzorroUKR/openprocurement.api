# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.cfaselectionua.tests.base import TenderContentWebTest, test_lots

from openprocurement.tender.belowthreshold.tests.document_blanks import (
    create_tender_document_error,
    create_tender_document_json_invalid,
    create_tender_document_json,
    put_tender_document_json,
    create_document_with_the_invalid_document_type,
    put_tender_json_document_of_document,
    create_lot_contract_proforma_document_json,
    create_lot_contract_proforma_document_json_invalid,
    create_lot_documents_by_registry_bot,
    create_lot_documents_by_registry_bot_invalid,
    create_lot_contract_data_document_json,
    upload_lot_document_by_renderer_bot,
    patch_tender_contract_proforma_document_invalid,
    put_tender_contract_proforma_document,
    upload_tender_document_contract_proforma_by_rbot_fail,
)

from openprocurement.tender.cfaselectionua.tests.document_blanks import (
    # TenderDocumentResourceTest
    not_found,
    create_document_active_tendering_status,
    create_document_active_enquiries_status,
    create_tender_document,
    put_tender_document,
    patch_tender_document,
)


class TenderDocumentResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_document = snitch(create_tender_document)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class TenderDocumentWithDSResourceTestMixin(object):
    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_put_tender_document_json = snitch(put_tender_document_json)
    test_create_document_with_the_invalid_document_type = snitch(create_document_with_the_invalid_document_type)
    test_put_tender_json_document_of_document = snitch(put_tender_json_document_of_document)
    test_patch_tender_contract_proforma_document_invalid = snitch(patch_tender_contract_proforma_document_invalid)
    test_put_tender_contract_proforma_document = snitch(put_tender_contract_proforma_document)
    test_upload_tender_document_contract_proforma_by_rbot_fail = \
        snitch(upload_tender_document_contract_proforma_by_rbot_fail)


class TenderDocumentResourceTest(TenderContentWebTest, TenderDocumentResourceTestMixin):

    initial_lots = test_lots
    initial_status = "active.enquiries"
    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)
    test_create_document_active_enquiries_status = snitch(create_document_active_enquiries_status)


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):

    initial_lots = test_lots
    docservice = True
    test_create_tender_document_error = snitch(create_tender_document_error)
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
