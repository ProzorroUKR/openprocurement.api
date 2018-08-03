# -*- coding: utf-8 -*-
import os
import unittest
from copy import deepcopy
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest, BaseDSAgreementWebTest
from openprocurement.agreement.cfaua.tests.base import TEST_AGREEMENT, TEST_DOCUMENTS


data = deepcopy(TEST_AGREEMENT)
data['documents'] = TEST_DOCUMENTS


class Base(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = data
    initial_auth = ('Basic', ('broker', ''))


class TestDocumentGet(Base):

    def test_get_documnets_list(self):
        resp = self.app.get(
            '/agreements/{}/documents'.format(self.agreement_id)
        )
        documents = resp.json['data']
        self.assertEqual(len(documents), len(TEST_DOCUMENTS))

    def test_get_documnet_by_id(self):
        documents = self.db.get(self.agreement_id).get('documents')
        for doc in documents:
            resp = self.app.get(
                '/agreements/{}/documents/{}'.format(self.agreement_id, doc['id'])
            )
            document = resp.json['data']
            self.assertEqual(doc['id'], document['id'])
            self.assertEqual(doc['title'], document['title'])
            self.assertEqual(doc['format'], document['format'])
            self.assertEqual(doc['datePublished'], document['datePublished'])


class BaseDS(BaseDSAgreementWebTest):
    initial_data = TEST_AGREEMENT
    relative_to = os.path.dirname(__file__)
    initial_auth = ('Basic', ('broker', ''))


class TestDocumentsCreate(BaseDS):

    def test_create_agreement_docuent_forbidden(self):
        response = self.app.post('/agreements/{}/documents'.format(
            self.agreement_id),
            upload_files=[('file', u'укр.doc', 'content')],
            status=403
        )
        self.assertEqual(response.status, '403 Forbidden')

    def test_create_agreement_documents(self):
        response = self.app.post('/agreements/{}/documents?acc_token={}'.format(
            self.agreement_id, self.agreement_token),
            upload_files=[('file', u'укр.doc', 'content')]
        )
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')


def suite():
    _suite = unittest.TestSuite()
    _suite.addTest(unittest.makeSuite(TestDocumentGet))
    _suite.addTest(unittest.makeSuite(TestDocumentsCreate))
    return _suite
