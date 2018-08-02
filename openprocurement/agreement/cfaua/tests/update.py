import os
import unittest
from openprocurement.agreement.core.tests.base import BaseAgreementWebTest
from openprocurement.agreement.cfaua.tests.base import TEST_AGREEMENT


class Base(BaseAgreementWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = TEST_AGREEMENT
    initial_auth = ('Basic', ('token', ''))


class TestExtractCredentials(Base):

    def test_extract_credentials(self):
        tender_token = self.initial_data['tender_token']
        response = self.app.get('/agreements/{}'.format(self.agreement_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.patch_json(
            '/agreements/{}?acc_token={}'.format(
                self.agreement_id, tender_token
            ),
            {"data": {"status": "active"}},
            status=403
        )
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.patch_json(
            '/agreements/{}/credentials?acc_token={}'.format(
                self.agreement_id, tender_token),
            {'data': ''}
        )
        self.assertEqual(response.status, '200 OK')
        self.assertIsNotNone(response.json.get('access', {}).get('token'))


# class TestAgreementPatch(Base):
#
#     def test_agreement_patch_invalid(self):
#         data = {
#             "status": "terminated",
#         }
#         response = self.app.patch_json(
#             '/agreements/{}/credentials?acc_token={}'.format(
#                 self.agreement_id, self.initial_data['tender_token']),
#             {'data': ''}
#         )
#         self.assertEqual(response.status, '200 OK')
#
#         token = response.json['access']['token']
#
#         responce = self.app.patch_json(
#             '/agreements/{}?acc_token={}'.format(
#             self.agreement_id, token),
#             {'data': data}
#         )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAgreementPatch))
    return suite