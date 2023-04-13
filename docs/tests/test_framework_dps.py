# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from tests.base.data import test_docs_tenderer
from tests.base.constants import DOCS_URL
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)

from openprocurement.api.utils import (
    get_now,
    parse_date,
)
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_data,
    BaseFrameworkWebTest,
)

TARGET_DIR = 'docs/source/frameworks/dps/tutorial/'

test_framework_open_data = deepcopy(test_framework_dps_data)


class FrameworkOpenResourceTest(BaseFrameworkWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_open_data
    docservice = True
    docservice_url = DOCS_URL

    def setUp(self):
        super(FrameworkOpenResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(FrameworkOpenResourceTest, self).tearDown()

    def create_framework(self):
        pass

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty frameworks listing
        self.initial_data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=60)).isoformat()
        response = self.app.get('/frameworks')
        self.assertEqual(response.json['data'], [])

        # create frameworks
        with open(TARGET_DIR + 'create-framework.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/frameworks', {
                    'data': self.initial_data,
                    'config': {
                        'restrictedDerivatives': False,
                    },
                }
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
                        "procuringEntity": {
                            "contactPoint": {
                                "telephone": "+0440000001"
                            }
                        },
                        "title": "updated in draft status"
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-framework-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/frameworks/{}/documents?acc_token={}'.format(
                    framework['id'], owner_token
                ),
                upload_files=[('file', 'framework.doc', b'content')]
            )

        with open(TARGET_DIR + 'framework-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/frameworks/{}/documents?acc_token={}'.format(
                    framework['id'], owner_token
                )
            )

        with open(TARGET_DIR + 'upload-framework-document-2.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/frameworks/{}/documents?acc_token={}'.format(
                    framework['id'], owner_token
                ),
                upload_files=[('file', 'framework_additional_docs.doc', b'additional info')]
            )

        doc_id = response.json['data']['id']

        with open(TARGET_DIR + 'upload-framework-document-3.http', 'w') as self.app.file_obj:
            response = self.app.put(
                '/frameworks/{}/documents/{}?acc_token={}'.format(
                    framework['id'], doc_id, owner_token
                ),
                upload_files=[('file', 'framework_additional_docs.doc', b'extended additional info')]
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
                }
            )
            self.assertEqual(response.status, '201 Created')

        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]

        with open(TARGET_DIR + 'upload-submission-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/submissions/{}/documents?acc_token={}'.format(self.submission_id, self.submission_token),
                upload_files=[('file', 'submission_docs.doc', b'additional info')]
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'get-submission-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/submissions/{}/documents'.format(self.submission_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-submission.http', 'w') as self.app.file_obj:
            response = self.app.get('/submissions/{}'.format(self.submission_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'updating-submission.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/submissions/{}?acc_token={}'.format(self.submission_id, self.submission_token),
                {'data': {"tenderers": [{"name": "НАЗВА"}]}},
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
            }
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
            response = self.app.get('/submissions'.format(self.framework_id))
            self.assertEqual(response.status, '200 OK')

        # Qualification

        with open(TARGET_DIR + 'get-qualification.http', 'w') as self.app.file_obj:
            response = self.app.get('/qualifications/{}'.format(self.qualification_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'upload-qualification-document.http', 'w') as self.app.file_obj:
            response = self.app.post(
                '/qualifications/{}/documents?acc_token={}'.format(
                    self.qualification_id, owner_token
                ),
                upload_files=[('file', 'qualification.doc', b'content')]
            )
            self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'qualification-documents.http', 'w') as self.app.file_obj:
            response = self.app.get(
                '/qualifications/{}/documents'.format(
                    self.qualification_id, owner_token
                )
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'get-qualification-documents.http', 'w') as self.app.file_obj:
            response = self.app.get('/qualifications/{}/documents'.format(self.qualification_id))
            self.assertEqual(response.status, '200 OK')

        # with open(TARGET_DIR + 'get-qualification.http', 'w') as self.app.file_obj:
        #     response = self.app.get('/qualifications/{}'.format(self.qualification_id))
        #     self.assertEqual(response.status, '200 OK')

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
            }
        )
        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]

        response = self.app.patch_json(
            '/submissions/{}?acc_token={}'.format(self.submission_id, self.submission_token),
            {'data': {"status": "active"}},
        )
        self.qualification_id = response.json["data"]["qualificationID"]

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
                            "contactPoint": {
                                "telephone": "+0440000002",
                                "name": "зміна",
                                "email": "ab@aa.com"
                            }
                        },
                        "description": "Назва предмета закупівлі1",
                        "qualificationPeriod": {
                            "endDate": new_endDate
                        }
                    }
                }
            )
            self.assertEqual(response.status, '200 OK')
