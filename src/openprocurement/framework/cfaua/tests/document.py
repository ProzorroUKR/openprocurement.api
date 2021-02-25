# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.framework.cfaua.tests.base import BaseAgreementContentWebTest, BaseDSAgreementContentWebTest
from openprocurement.framework.cfaua.tests.data import TEST_AGREEMENT, TEST_DOCUMENTS
from openprocurement.framework.cfaua.tests.document_blanks import (
    get_documents_list,
    get_document_by_id,
    create_agreement_document_forbidden,
    create_agreement_documents,
    not_found,
    put_contract_document,
)


class TestDocumentGet(BaseAgreementContentWebTest):
    initial_data = deepcopy(TEST_AGREEMENT)
    initial_data["documents"] = TEST_DOCUMENTS

    test_get_documnets_list = snitch(get_documents_list)
    test_get_documnet_by_id = snitch(get_document_by_id)


class TestDocumentsCreate(BaseDSAgreementContentWebTest):
    initial_data = TEST_AGREEMENT

    test_create_agreement_document_forbidden = snitch(create_agreement_document_forbidden)
    test_create_agreement_documents = snitch(create_agreement_documents)


class AgreementDocumentWithDSResourceTest(BaseDSAgreementContentWebTest):
    initial_data = TEST_AGREEMENT

    test_not_found = snitch(not_found)
    test_put_contract_document = snitch(put_contract_document)


def suite():
    _suite = unittest.TestSuite()
    _suite.addTest(unittest.makeSuite(TestDocumentGet))
    _suite.addTest(unittest.makeSuite(TestDocumentsCreate))
    _suite.addTest(unittest.makeSuite(AgreementDocumentWithDSResourceTest))
    return _suite
