# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest
from openprocurement.tender.openeu.tests.document_blanks import (
    # TenderDocumentWithDSResourceTest
    create_tender_document_json_invalid,
    create_tender_document_json,
    put_tender_document_json,
    # TenderDocumentResourceTest
    not_found,
    create_tender_document,
    put_tender_document,
    patch_tender_document,
)


class TenderDocumentResourceTest(BaseTenderContentWebTest):
    docservice = False

    initial_auth = ('Basic', ('broker', ''))

    test_not_found = snitch(not_found)
    test_create_tender_document = snitch(create_tender_document)
    test_put_tender_document = snitch(put_tender_document)
    test_patch_tender_document = snitch(patch_tender_document)


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest):
    docservice = True

    test_create_tender_document_json_invalid = snitch(create_tender_document_json_invalid)
    test_create_tender_document_json = snitch(create_tender_document_json)
    test_put_tender_document_json = snitch(put_tender_document_json)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
