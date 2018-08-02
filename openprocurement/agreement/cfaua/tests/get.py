import os
import unittest
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest
from openprocurement.agreement.cfaua.tests.base import TEST_AGREEMENT


class AgreementResourceTest(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT
    initial_auth = ('Basic', ('broker', ''))

    def test_get_agreement(self):
        resp = self.app.get('/agreements/{}'.format(
            self.agreement_id
        ))
        self.assertEqual(
            resp.status,
            '200 OK'
        )
