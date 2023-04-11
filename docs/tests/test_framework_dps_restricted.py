# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.tests.base import change_auth
from tests.base.data import (
    test_docs_tenderer,
    test_docs_tenderer2,
)
from tests.base.constants import DOCS_URL
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)

from openprocurement.api.utils import get_now
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_data,
    BaseFrameworkWebTest,
)

TARGET_DIR = 'docs/source/frameworks/basic-actions/http/restricted/'

test_framework_open_data = deepcopy(test_framework_dps_data)


class RestrictedFrameworkOpenResourceTest(BaseFrameworkWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_open_data
    docservice = True
    docservice_url = DOCS_URL

    def setUp(self):
        super(RestrictedFrameworkOpenResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(RestrictedFrameworkOpenResourceTest, self).tearDown()

    def create_framework(self):
        pass

    def test_docs(self):
        # empty frameworks listing
        data = deepcopy(self.initial_data)
        data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=60)).isoformat()
        data["procuringEntity"]["kind"] = "defense"
        response = self.app.get('/frameworks')
        self.assertEqual(response.json['data'], [])

        # create frameworks
        with change_auth(self.app, ("Basic", ("broker", ""))):
            with open(TARGET_DIR + 'framework-create-broker.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/frameworks', {
                        'data': data,
                        'config': {
                            'restrictedDerivatives': True,
                        }
                    }
                )
                self.assertEqual(response.status, '201 Created')

            framework = response.json['data']
            self.framework_id = framework["id"]
            owner_token = response.json['access']['token']

            with open(TARGET_DIR + 'framework-activate-broker.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/frameworks/{}?acc_token={}'.format(framework['id'], owner_token), {'data': {"status": "active"}}
                )
                self.assertEqual(response.status, '200 OK')

        # Speed up time
        self.tick(delta=timedelta(days=16))

        # Submissions

        # Create by Broker 1
        with change_auth(self.app, ("Basic", ("broker1", ""))):
            with open(TARGET_DIR + 'submission-register-broker1.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/submissions',
                    {
                        'data': {
                            "tenderers": [test_docs_tenderer],
                            "frameworkID": self.framework_id,
                        },
                        'config': {
                            'restricted': True,
                        },
                    }
                )
                self.assertEqual(response.status, '201 Created')

            self.submission1_id = response.json["data"]["id"]
            self.submission1_token = response.json["access"]["token"]

            with open(TARGET_DIR + 'submission-activate-broker1.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/submissions/{}?acc_token={}'.format(self.submission1_id, self.submission1_token),
                    {'data': {"status": "active"}},
                )
                self.assertEqual(response.status, '200 OK')

            self.qualification1_id = response.json["data"]["qualificationID"]

        # Create by Broker 2
        with change_auth(self.app, ("Basic", ("broker2", ""))):
            with open(TARGET_DIR + 'submission-register-broker2.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/submissions',
                    {
                        'data': {
                            "tenderers": [test_docs_tenderer2],
                            "frameworkID": self.framework_id,
                        },
                        'config': {
                            'restricted': True,
                        },
                    }
                )
                self.assertEqual(response.status, '201 Created')

            self.submission2_id = response.json["data"]["id"]
            self.submission2_token = response.json["access"]["token"]

            with open(TARGET_DIR + 'submission-activate-broker2.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/submissions/{}?acc_token={}'.format(self.submission2_id, self.submission2_token),
                    {'data': {"status": "active"}},
                )
                self.assertEqual(response.status, '200 OK')

            self.qualification2_id = response.json["data"]["qualificationID"]

        # Check by Broker (Procuring Entity) can see all submissions
        with change_auth(self.app, ("Basic", ("broker", ""))):
            with open(TARGET_DIR + 'submission-feed-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'submission-get-1-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission1_id))
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'submission-get-2-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission2_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Broker 1
        with change_auth(self.app, ("Basic", ("broker1", ""))):
            with open(TARGET_DIR + 'submission-feed-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'submission-get-1-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission1_id))
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'submission-get-2-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission2_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

        # Check by Broker 2
        with change_auth(self.app, ("Basic", ("broker2", ""))):
            with open(TARGET_DIR + 'submission-feed-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'submission-get-1-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission1_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

            with open(TARGET_DIR + 'submission-get-2-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission2_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Anonymous
        with change_auth(self.app, None):
            with open(TARGET_DIR + 'submission-feed-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'submission-get-1-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission1_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

            with open(TARGET_DIR + 'submission-get-2-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/submissions/{}'.format(self.submission2_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

        # Qualification

        # Check by Broker (Procuring Entity) can see all qualifications
        with change_auth(self.app, ("Basic", ("broker", ""))):
            with open(TARGET_DIR + 'qualification-feed-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-get-1-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification1_id))
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-get-2-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification2_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Broker 1
        with change_auth(self.app, ("Basic", ("broker1", ""))):
            with open(TARGET_DIR + 'qualification-feed-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-get-1-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification1_id))
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-get-2-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification2_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

        # Check by Broker 2
        with change_auth(self.app, ("Basic", ("broker2", ""))):
            with open(TARGET_DIR + 'qualification-feed-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-get-1-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification1_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

            with open(TARGET_DIR + 'qualification-get-2-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification2_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Anonymous
        with change_auth(self.app, None):
            with open(TARGET_DIR + 'qualification-feed-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications?opt_fields=frameworkID,status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-get-1-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification1_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

            with open(TARGET_DIR + 'qualification-get-2-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/qualifications/{}'.format(self.qualification2_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

        # Activate Qualifications
        with change_auth(self.app, ("Basic", ("broker", ""))):
            with open(TARGET_DIR + 'qualification-activate-1-broker.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/qualifications/{}?acc_token={}'.format(self.qualification1_id, owner_token),
                    {'data': {"status": "active"}},
                )
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'qualification-activate-2-broker.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/qualifications/{}?acc_token={}'.format(self.qualification2_id, owner_token),
                    {'data': {"status": "active"}},
                )
                self.assertEqual(response.status, '200 OK')

        # Qualification

        with change_auth(self.app, None):
            with open(TARGET_DIR + 'framework-with-agreement.http', 'w') as self.app.file_obj:
                response = self.app.get(f'/frameworks/{self.framework_id}')
                self.assertEqual(response.status, '200 OK')
                self.agreement_id = response.json["data"]["agreementID"]

        # Check by Broker (Procuring Entity)
        with change_auth(self.app, ("Basic", ("broker", ""))):
            with open(TARGET_DIR + 'agreement-feed-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements?opt_fields=status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'agreement-get-broker.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements/{}'.format(self.agreement_id))
                self.assertEqual(response.status, '200 OK')

        # Check by Broker 1
        with change_auth(self.app, ("Basic", ("broker1", ""))):
            with open(TARGET_DIR + 'agreement-feed-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements?opt_fields=status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'agreement-get-broker1.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements/{}'.format(self.agreement_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

        # Check by Broker 2
        with change_auth(self.app, ("Basic", ("broker2", ""))):
            with open(TARGET_DIR + 'agreement-feed-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements?opt_fields=status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'agreement-get-broker2.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements/{}'.format(self.agreement_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')

        # Check by Anonymous
        with change_auth(self.app, None):
            with open(TARGET_DIR + 'agreement-feed-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements?opt_fields=status')
                self.assertEqual(response.status, '200 OK')

            with open(TARGET_DIR + 'agreement-get-anonymous.http', 'w') as self.app.file_obj:
                response = self.app.get('/agreements/{}'.format(self.agreement_id), status=403)
                self.assertEqual(response.status, '403 Forbidden')
