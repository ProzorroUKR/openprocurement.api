# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.document import (
    TenderDocumentResourceTestMixin,
    TenderDocumentWithDSResourceTestMixin,
    create_lot_contract_proforma_document_json,
    create_lot_contract_proforma_document_json_invalid,
)

from openprocurement.tender.cfaua.tests.base import BaseTenderContentWebTest


class TenderDocumentResourceTest(BaseTenderContentWebTest, TenderDocumentResourceTestMixin):
    docservice = False
    initial_auth = ("Basic", ("broker", ""))


class TenderDocumentWithDSResourceTest(TenderDocumentResourceTest, TenderDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_tender_contract_proforma_document_json = snitch(create_lot_contract_proforma_document_json)
    test_create_tender_contract_proforma_document_json_invalid = snitch(create_lot_contract_proforma_document_json_invalid)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
