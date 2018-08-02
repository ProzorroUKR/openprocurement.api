import os
import unittest
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest
from openprocurement.agreement.cfaua.tests.base import TEST_AGREEMENT


class Base(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT
    initial_auth = ('Basic', ('broker', ''))


class AgreementResourceTest(Base):

    def test_get_agreement(self):
        resp = self.app.get('/agreements/{}'.format(
            self.agreement_id
        ))
        self.assertEqual(
            resp.status,
            '200 OK'
        )


class AgreementContractsResourceTest(Base):
    def test_get_agreement_contracts(self):
        resp = self.app.get('/agreements/{}/contracts'.format(
            self.agreement_id
        ))
        self.assertEqual(
            resp.status,
            '200 OK'
        )


class AgreementDocumentsResourceTest(Base):
    def test_get_agreement_documents(self):
        resp = self.app.get('/agreements/{}/documents'.format(
            self.agreement_id
        ))
        self.assertEqual(
            resp.status,
            '200 OK'
        )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AgreementResourceTest))
    suite.addTest(unittest.makeSuite(AgreementContractsResourceTest))
    suite.addTest(unittest.makeSuite(AgreementDocumentsResourceTest))
    return suite
