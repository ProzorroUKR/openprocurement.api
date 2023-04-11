# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_lots,
)

from openprocurement.tender.belowthreshold.tests.document_blanks import (
    create_tender_document_json_invalid,
    create_tender_document_json,
    create_tender_document_json_bulk,
    put_tender_document_json,
)

from openprocurement.tender.cfaselectionua.tests.document_blanks import (
    not_found,
    create_document_active_tendering_status,
    create_document_active_enquiries_status,
    create_tender_document,
    put_tender_document,
    patch_tender_document,
)


class TenderDocumentWithDSResourceTestMixin(object):
    test_not_found = snitch(not_found)
    test_create_tender_document = snitch(create_tender_document)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)
    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_create_tender_document_json_bulk = snitch(create_tender_document_json_bulk)
    test_put_tender_document_json = snitch(put_tender_document_json)


class TenderDocumentWithDSResourceTest(TenderContentWebTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True
    initial_lots = test_tender_cfaselectionua_lots
    initial_status = "active.enquiries"
    test_create_document_active_tendering_status = snitch(create_document_active_tendering_status)
    test_create_document_active_enquiries_status = snitch(create_document_active_enquiries_status)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
