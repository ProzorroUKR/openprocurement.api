# -*- coding: utf-8 -*-
import os
import unittest
from copy import deepcopy

from openprocurement.agreement.cfaua.tests.document_blanks import (
    get_documents_list,
    get_document_by_id,
    create_agreement_document_forbidden,
    create_agreement_documents,
    not_found,
    put_contract_document
)
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest, BaseDSAgreementWebTest
from openprocurement.agreement.cfaua.tests.base import TEST_AGREEMENT, TEST_DOCUMENTS
from openprocurement.api.tests.base import snitch

data = deepcopy(TEST_AGREEMENT)
data['documents'] = TEST_DOCUMENTS


class Base(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = data
    initial_auth = ('Basic', ('broker', ''))


class TestDocumentGet(Base):
    test_get_documnets_list = snitch(get_documents_list)
    test_get_documnet_by_id = snitch(get_document_by_id)


class BaseDS(BaseDSAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT
    initial_auth = ('Basic', ('broker', ''))


class TestDocumentsCreate(BaseDS):
    test_create_agreement_document_forbidden = snitch(create_agreement_document_forbidden)
    test_create_agreement_documents = snitch(create_agreement_documents)


class AgreementDocumentWithDSResourceTest(BaseDS):
    test_not_found = snitch(not_found)
    test_put_contract_document = snitch(put_contract_document)


def suite():
    _suite = unittest.TestSuite()
    _suite.addTest(unittest.makeSuite(TestDocumentGet))
    _suite.addTest(unittest.makeSuite(TestDocumentsCreate))
    _suite.addTest(unittest.makeSuite(AgreementDocumentWithDSResourceTest))
    return _suite
