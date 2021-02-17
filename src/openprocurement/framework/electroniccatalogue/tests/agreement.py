import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.framework.electroniccatalogue.tests.agreement_blanks import create_agreement, change_agreement
from openprocurement.framework.electroniccatalogue.tests.base import test_electronicCatalogue_data, test_submission_data
from openprocurement.framework.electroniccatalogue.tests.qualification import (
    QualificationContentWebTest as BaseQualificationContentWebTest,
)


class QualificationContentWebTest(BaseQualificationContentWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.post(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            upload_files=[("file", "name  name.doc", b"content")]
        )
        self.assertEqual(response.status, "201 Created")


class AgreementContentWebTest(QualificationContentWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.post(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            upload_files=[("file", "name  name.doc", b"content")]
        )
        self.assertEqual(response.status, "201 Created")

        response = self.app.patch_json(
            f"/qualifications/{self.qualification_id}?acc_token={self.framework_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.get(f"/frameworks/{self.framework_id}")
        self.assertEqual(response.status, "200 OK")

        self.agreement_id = self.agreement_id = response.json["data"]["agreementID"]


class TestAgreementCreation(QualificationContentWebTest):
    initial_data = test_electronicCatalogue_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))
    docservice = True

    test_create_agreement = snitch(create_agreement)


class TestAgreementChanges(AgreementContentWebTest):
    initial_data = test_electronicCatalogue_data
    initial_submission_data = test_submission_data
    initial_auth = ('Basic', ('broker', ''))

    test_change_agreement = snitch(change_agreement)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAgreementCreation)
    suite.addTest(TestAgreementChanges)


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
