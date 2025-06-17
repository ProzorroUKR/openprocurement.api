import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.core.tests.document_blanks import (
    contract_change_document,
    create_contract_document,
    create_contract_document_json,
    create_contract_document_json_invalid,
    create_contract_transaction_document_json,
    limited_contract_confidential_document,
    not_found,
    patch_contract_document,
    put_contract_document,
    put_contract_document_json,
)
from openprocurement.contracting.econtract.tests.base import BaseEContractContentWebTest
from openprocurement.contracting.econtract.tests.document_blanks import (
    activate_contract_after_signatures_and_document_upload,
    patch_contract_signature_by_another_user,
    patch_contract_signature_duplicate,
    patch_signature_in_active_contract,
    sign_active_contract,
    sign_pending_contract,
)


class ContractDocumentResourceTest(BaseEContractContentWebTest):
    test_not_found = snitch(not_found)
    test_create_contract_documnet = snitch(create_contract_document)
    test_put_contract_document = snitch(put_contract_document)
    test_patch_contract_document = snitch(patch_contract_document)
    test_contract_change_document = snitch(contract_change_document)
    test_create_contract_document_json_invalid = snitch(create_contract_document_json_invalid)
    test_create_contract_document_json = snitch(create_contract_document_json)
    test_put_contract_document_json = snitch(put_contract_document_json)
    test_create_contract_transaction_document_json = snitch(create_contract_transaction_document_json)
    test_limited_contract_confidential_document = snitch(limited_contract_confidential_document)
    test_sign_pending_contract = snitch(sign_pending_contract)
    test_sign_active_contract = snitch(sign_active_contract)
    test_patch_signature_in_active_contract = snitch(patch_signature_in_active_contract)
    test_patch_contract_signature_by_another_user = snitch(patch_contract_signature_by_another_user)
    test_patch_contract_signature_duplicate = snitch(patch_contract_signature_duplicate)
    test_activate_contract_after_signatures_and_document_upload = snitch(
        activate_contract_after_signatures_and_document_upload
    )
    # test_add_document_by_supplier = snitch(add_document_by_supplier)
    # test_patch_signature_document_type_by_supplier = snitch(patch_signature_document_type_by_supplier)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
