# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.document_blanks import (
    # TenderDocument ResourceTest
    not_found,
    create_tender_document,
    put_tender_document,
    patch_tender_document,
    # TenderDocumentResourceTest
    create_tender_document_json_invalid,
    create_tender_document_json,
    create_tender_document_json_bulk,
    put_tender_document_json,
)

from openprocurement.tender.simpledefense.tests.base import BaseSimpleDefContentWebTest


class TenderDocumentResourceTest(BaseSimpleDefContentWebTest):
    docservice = False

    test_not_found = snitch(not_found)
    test_create_tender_document = snitch(create_tender_document)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest):
    docservice = True

    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_create_tender_document_json_bulk = snitch(create_tender_document_json_bulk)
    test_put_tender_document_json = snitch(put_tender_document_json)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
