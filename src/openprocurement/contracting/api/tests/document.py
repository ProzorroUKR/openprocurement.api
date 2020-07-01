# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.contracting.api.tests.base import BaseContractContentWebTest
from openprocurement.contracting.api.tests.document_blanks import (
    not_found,
    create_contract_document,
    put_contract_document,
    patch_contract_document,
    contract_change_document,
    create_contract_document_json_invalid,
    create_contract_document_json,
    put_contract_document_json,
    create_contract_transaction_document_json
)


class ContractDocumentResourceTest(BaseContractContentWebTest):
    docservice = False

    test_not_found = snitch(not_found)
    test_create_contract_documnet = snitch(create_contract_document)
    test_put_contract_document = snitch(put_contract_document)
    test_patch_contract_document = snitch(patch_contract_document)
    test_contract_change_document = snitch(contract_change_document)


class ContractDocumentWithDSResourceTest(ContractDocumentResourceTest):
    docservice = True

    test_create_contract_documnet_json_invalid = snitch(create_contract_document_json_invalid)
    test_create_contract_documnet_json = snitch(create_contract_document_json)
    test_put_contract_document_json = snitch(put_contract_document_json)
    test_create_contract_transaction_document_json = snitch(create_contract_transaction_document_json)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(ContractDocumentWithDSResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
