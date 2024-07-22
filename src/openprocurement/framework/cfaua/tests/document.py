import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.cfaua.tests.base import BaseAgreementContentWebTest
from openprocurement.framework.cfaua.tests.data import TEST_AGREEMENT, TEST_DOCUMENTS
from openprocurement.framework.cfaua.tests.document_blanks import (
    create_agreement_document_forbidden,
    create_agreement_documents,
    document_related_item,
    get_document_by_id,
    get_documents_list,
    not_found,
    put_contract_document,
)


class TestDocumentGet(BaseAgreementContentWebTest):
    initial_data = deepcopy(TEST_AGREEMENT)
    initial_data["documents"] = TEST_DOCUMENTS

    test_get_documnets_list = snitch(get_documents_list)
    test_get_documnet_by_id = snitch(get_document_by_id)


class TestDocumentsCreate(BaseAgreementContentWebTest):
    initial_data = TEST_AGREEMENT

    test_create_agreement_document_forbidden = snitch(create_agreement_document_forbidden)
    test_create_agreement_documents = snitch(create_agreement_documents)


class AgreementDocumentResourceTest(BaseAgreementContentWebTest):
    initial_data = TEST_AGREEMENT

    test_not_found = snitch(not_found)
    test_put_contract_document = snitch(put_contract_document)
    test_document_related_item = snitch(document_related_item)


def suite():
    _suite = unittest.TestSuite()
    _suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestDocumentGet))
    _suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestDocumentsCreate))
    return _suite
