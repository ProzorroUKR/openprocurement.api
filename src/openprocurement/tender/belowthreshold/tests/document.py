import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.document_blanks import (
    create_document_active_tendering_status,
    create_tender_document,
    create_tender_document_json,
    create_tender_document_json_bulk,
    create_tender_document_json_invalid,
    delete_tender_document,
    lot_patch_tender_document_json_items_none,
    lot_patch_tender_document_json_lots_none,
    not_found,
    patch_tender_document,
    put_tender_document,
    put_tender_document_json,
    tender_confidential_documents,
    tender_notice_documents,
)


class TenderDocumentResourceTestMixin:
    test_not_found = snitch(not_found)
    test_create_tender_document = snitch(create_tender_document)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)
    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_create_tender_document_json_bulk = snitch(create_tender_document_json_bulk)
    test_put_tender_document_json = snitch(put_tender_document_json)
    test_tender_notice_documents = snitch(tender_notice_documents)
    test_tender_confidential_documents = snitch(tender_confidential_documents)
    test_delete_tender_document = snitch(delete_tender_document)


class TenderDocumentResourceTest(TenderContentWebTest, TenderDocumentResourceTestMixin):
    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)


class TenderLotDocumentResourceTest(TenderContentWebTest):
    initial_lots = test_tender_below_lots

    test_lot_patch_tender_document_json_lots_none = snitch(lot_patch_tender_document_json_lots_none)
    test_lot_patch_tender_document_json_items_none = snitch(lot_patch_tender_document_json_items_none)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
