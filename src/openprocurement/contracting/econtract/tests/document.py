import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.core.tests.document_blanks import (
    create_contract_document_json_invalid,
    create_contract_transaction_document_json,
    limited_contract_confidential_document,
    not_found,
)
from openprocurement.contracting.econtract.tests.base import BaseEContractContentWebTest
from openprocurement.contracting.econtract.tests.document_blanks import (
    activate_contract_after_signatures_and_document_upload,
    create_contract_document,
    create_contract_document_json,
    post_contract_signature_duplicate,
    sign_active_contract,
    sign_pending_contract,
)


class ContractDocumentResourceTest(BaseEContractContentWebTest):
    test_not_found = snitch(not_found)
    test_create_contract_document = snitch(create_contract_document)
    test_create_contract_document_json_invalid = snitch(create_contract_document_json_invalid)
    test_create_contract_document_json = snitch(create_contract_document_json)
    test_create_contract_transaction_document_json = snitch(create_contract_transaction_document_json)
    test_limited_contract_confidential_document = snitch(limited_contract_confidential_document)
    test_sign_pending_contract = snitch(sign_pending_contract)
    test_sign_active_contract = snitch(sign_active_contract)
    test_post_contract_signature_duplicate = snitch(post_contract_signature_duplicate)
    test_activate_contract_after_signatures_and_document_upload = snitch(
        activate_contract_after_signatures_and_document_upload
    )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
