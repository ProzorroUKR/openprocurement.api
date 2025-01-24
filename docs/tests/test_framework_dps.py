import os
from copy import deepcopy
from datetime import timedelta

from tests.base.constants import DOCS_URL
from tests.base.data import test_docs_tenderer
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.framework.dps.tests.base import (
    BaseFrameworkWebTest,
    test_framework_dps_config,
    test_framework_dps_data,
)

TARGET_DIR = 'docs/source/frameworks/dps/tutorial/'

test_framework_dps_data = deepcopy(test_framework_dps_data)


class FrameworkDPSResourceTest(BaseFrameworkWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_dps_data
    initial_config = test_framework_dps_config
    docservice_url = DOCS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty frameworks listing
        self.initial_data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=60)).isoformat()
        response = self.app.get('/frameworks')
        self.assertEqual(response.json['data'], [])

        # create frameworks
        with open(TARGET_DIR + 'create-framework.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/frameworks',
                {'data': self.initial_data, 'config': self.initial_config},
            )
            self.assertEqual(response.status, '201 Created')

        framework = response.json['data']
        self.framework_id = framework["id"]
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'patch-framework-draft.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token),
                {
                    'data': {
                        "procuringEntity": {"contactPoint": {"telephone": "+0440000001"}},
                        "title": "updated in draft status",
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-framework-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/frameworks/{}/documents?acc_token={}'.format(framework['id'], owner_token),
                {
                    "data": {
                        "title": "framework.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )

        with open(TARGET_DIR + 'framework-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks/{}/documents?acc_token={}'.format(framework['id'], owner_token))

        with open(TARGET_DIR + 'upload-framework-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/frameworks/{}/documents?acc_token={}'.format(framework['id'], owner_token),
                {
                    "data": {
                        "title": "framework_additional_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )

        doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'upload-framework-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put_json(
                '/frameworks/{}/documents/{}?acc_token={}'.format(framework['id'], doc_id, owner_token),
                {
                    "data": {
                        "title": "framework_additional_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )

        with open(TARGET_DIR + 'get-framework-document-3.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/frameworks/{}/documents/{}?acc_token={}'.format(framework['id'], doc_id, owner_token)
            )

        with open(TARGET_DIR + 'patch-framework-draft-to-active.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token), {'data': {"status": "active"}}
            )
            self.assertEqual(response.status, '200 OK')

        # Submissions
        self.tick(delta=timedelta(days=16))
        with open(TARGET_DIR + 'register-submission.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/submissions',
                {
                    'data': {
                        "tenderers": [test_docs_tenderer],
                        "frameworkID": self.framework_id,
                    },
                    'config': {
                        'restricted': False,
                    },
                },
            )
            self.assertEqual(response.status, '201 Created')

        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]

        with open(TARGET_DIR + 'upload-submission-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/submissions/{}/documents?acc_token={}'.format(self.submission_id, self.submission_token),
                {
                    "data": {
                        "title": "submission_docs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'get-submission-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/submissions/{}/documents'.format(self.submission_id))
            self.assertEqual(response.status, '200 OK')

        # add confidential doc without rationale
        with open(TARGET_DIR + 'upload-submission-conf-docs-wo-rationale.http', 'w') as self.app.file_obj:
            self.app.post_json(
                f'/submissions/{self.submission_id}/documents?acc_token={self.submission_token}',
                {
                    'data': {
                        "title": "specs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "technicalSpecifications",
                        "confidentiality": "buyerOnly",
                    },
                },
                status=422,
            )
        with open(TARGET_DIR + 'upload-submission-conf-docs.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/submissions/{self.submission_id}/documents?acc_token={self.submission_token}',
                {
                    'data': {
                        "title": "specs.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                        "documentType": "technicalSpecifications",
                        "confidentiality": "buyerOnly",
                        "confidentialityRationale": "Дуже конфіденційний файл, треба приховати",
                    },
                },
            )
            self.assertEqual(response.status, '201 Created')
            doc_id = response.json["data"]["id"]

        # get doc directly as tender owner
        with open(TARGET_DIR + 'get-submission-conf-docs-by-owner.http', 'w') as self.app.file_obj:
            response = self.app.get(
                f'/submissions/{self.submission_id}/documents/{doc_id}?acc_token={self.submission_token}',
            )
            self.assertIn("url", response.json["data"])

        # get doc directly as public
        with open(TARGET_DIR + 'get-submission-conf-docs-by-public.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/submissions/{self.submission_id}/documents/{doc_id}')
            self.assertNotIn("url", response.json["data"])

        # download as tender public
        with open(TARGET_DIR + 'upload-submission-conf-doc-by-public.http', 'w') as self.app.file_obj:
            self.app.get(
                f"/submissions/{self.submission_id}/documents/{doc_id}?download=1",
                status=403,
            )

        with open(TARGET_DIR + 'get-submission.http', 'w') as self.app.file_obj:
            response = self.app.get('/submissions/{}'.format(self.submission_id))
            self.assertEqual(response.status, '200 OK')

        tenderer = deepcopy(test_docs_tenderer)
        tenderer["name"] = "НАЗВА"
        with open(TARGET_DIR + 'updating-submission.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/submissions/{}?acc_token={}'.format(self.submission_id, self.submission_token),
                {'data': {"tenderers": [tenderer]}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'deleting-submission.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/submissions/{}?acc_token={}'.format(self.submission_id, self.submission_token),
                {'data': {"status": "deleted"}},
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/submissions'.format(self.submission_id, self.submission_token),
            {
                'data': {
                    "tenderers": [test_docs_tenderer],
                    "frameworkID": self.framework_id,
                },
                'config': {
                    'restricted': False,
                },
            },
        )
        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]

        with open(TARGET_DIR + 'activating-submission.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/submissions/{}?acc_token={}'.format(self.submission_id, self.submission_token),
                {'data': {"status": "active"}},
            )
            self.assertEqual(response.status, '200 OK')

        self.qualification_id = response.json["data"]["qualificationID"]

        with open(TARGET_DIR + 'submission-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/submissions')
            self.assertEqual(response.status, '200 OK')

        # Qualification

        with open(TARGET_DIR + 'get-qualification.http', 'w') as self.app.file_obj:
            response = self.app.get('/qualifications/{}'.format(self.qualification_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-qualification-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/qualifications/{}/documents?acc_token={}'.format(self.qualification_id, owner_token),
                {
                    "data": {
                        "title": "qualification.doc",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/msword",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'qualification-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/qualifications/{}/documents'.format(self.qualification_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-qualification-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/qualifications/{}/documents'.format(self.qualification_id))
            self.assertEqual(response.status, '200 OK')

        # with open(TARGET_DIR + 'get-qualification.http', 'w') as self.app.file_obj:
        #     response = self.app.get('/qualifications/{}'.format(self.qualification_id))
        #     self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'evaluation-reports-document-required-for-cancelling.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f'/qualifications/{self.qualification_id}?acc_token={owner_token}',
                {'data': {"status": "unsuccessful"}},
                status=422,
            )

        with open(TARGET_DIR + 'add-evaluation-reports-document-for-cancelling.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/qualifications/{self.qualification_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "sign.p7s",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pkcs7-signature",
                        "documentType": "evaluationReports",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'unsuccessful-qualification.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/qualifications/{}?acc_token={}'.format(self.qualification_id, owner_token),
                {'data': {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/submissions'.format(self.submission_id, self.submission_token),
            {
                'data': {
                    "tenderers": [test_docs_tenderer],
                    "frameworkID": self.framework_id,
                },
                'config': {
                    'restricted': False,
                },
            },
        )
        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]

        response = self.app.patch_json(
            '/submissions/{}?acc_token={}'.format(self.submission_id, self.submission_token),
            {'data': {"status": "active"}},
        )
        self.qualification_id = response.json["data"]["qualificationID"]
        with open(TARGET_DIR + 'evaluation-reports-document-required.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                f'/qualifications/{self.qualification_id}?acc_token={owner_token}',
                {'data': {"status": "active"}},
                status=422,
            )

        with open(TARGET_DIR + 'add-evaluation-reports-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/qualifications/{self.qualification_id}/documents?acc_token={owner_token}',
                {
                    "data": {
                        "title": "sign.p7s",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pkcs7-signature",
                        "documentType": "evaluationReports",
                    }
                },
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'activation-qualification.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/qualifications/{}?acc_token={}'.format(self.qualification_id, owner_token),
                {'data': {"status": "active"}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-framework-with-agreement.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/frameworks/{self.framework_id}')
            self.assertEqual(response.status, '200 OK')
            agreement_id = response.json["data"]["agreementID"]

        with open(TARGET_DIR + 'get-agreement.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/agreements/{agreement_id}')
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'agreement-listing.http', 'w') as self.app.file_obj:
            response = self.app.get(f'/agreements')
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-submissions-by-framework-id.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks/{}/submissions'.format(self.framework_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-qualifications-by-framework-id.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks/{}/qualifications'.format(self.framework_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'qualification-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/qualifications'.format(self.framework_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-framework.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks/{}'.format(framework['id']))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'framework-listing.http', 'w') as self.app.file_obj:
            response = self.app.get('/frameworks'.format(framework['id']))
            self.assertEqual(len(response.json['data']), 1)

        with open(TARGET_DIR + 'patch-framework-active.http', 'w') as self.app.file_obj:
            new_endDate = (parse_date(framework["qualificationPeriod"]["endDate"]) + timedelta(days=15)).isoformat()
            response = self.app.patch_json(
                '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token),
                {
                    'data': {
                        "procuringEntity": {
                            "contactPoint": {"telephone": "+0440000002", "name": "зміна", "email": "ab@aa.com"}
                        },
                        "description": "Назва предмета закупівлі1",
                        "qualificationPeriod": {"endDate": new_endDate},
                    }
                },
            )
            self.assertEqual(response.status, '200 OK')
