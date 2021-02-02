# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import TenderContentWebTest, test_lots
from openprocurement.tender.belowthreshold.tests.document_blanks import (
    # TenderDocumentResourceTest
    not_found,
    create_document_active_tendering_status,
    create_tender_document,
    put_tender_document,
    patch_tender_document,
    # TenderDocumentWithDSResourceTest
    create_tender_document_error,
    create_tender_document_json_invalid,
    create_tender_document_json,
    create_tender_document_json_bulk,
    put_tender_document_json,
    # TenderLotDocumentWithDSResourceTest
    lot_patch_tender_document_json_lots_none,
    lot_patch_tender_document_json_items_none,
)


class TenderDocumentResourceTestMixin:
    test_not_found = snitch(not_found)
    test_create_tender_document = snitch(create_tender_document)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class TenderDocumentWithDSResourceTestMixin:
    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_create_tender_document_json_bulk = snitch(create_tender_document_json_bulk)
    test_put_tender_document_json = snitch(put_tender_document_json)


class TenderDocumentResourceTest(TenderContentWebTest, TenderDocumentResourceTestMixin):
    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_tender_document_error = snitch(create_tender_document_error)


class TenderLotDocumentWithDSResourceTest(TenderContentWebTest):
    initial_lots = test_lots
    docservice = True

    test_lot_patch_tender_document_json_lots_none = snitch(lot_patch_tender_document_json_lots_none)
    test_lot_patch_tender_document_json_items_none = snitch(lot_patch_tender_document_json_items_none)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
