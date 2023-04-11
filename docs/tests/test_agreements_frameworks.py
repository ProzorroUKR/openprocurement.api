# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.electroniccatalogue.tests.base import (
    test_framework_electronic_catalogue_data,
    ban_milestone_data_with_documents,
    BaseFrameworkWebTest,
)

from tests.base.data import test_docs_tenderer
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.base.constants import DOCS_URL

TARGET_DIR = "docs/source/agreements/frameworks/http/"


class FrameworkAgreementResourceTest(BaseFrameworkWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_electronic_catalogue_data
    docservice = True
    docservice_url = DOCS_URL

    def setUp(self):
        super(FrameworkAgreementResourceTest, self).setUp()
        self.setUpMock()
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data["qualificationPeriod"] = {"endDate": (get_now() + timedelta(days=120)).isoformat()}

    def tearDown(self):
        self.tearDownMock()
        super(FrameworkAgreementResourceTest, self).tearDown()

    def test_docs(self):
        self.create_framework()
        auth = self.app.authorization
        self.activate_framework()

        self.app.authorization = ('Basic', ('broker', ''))

        response = self.app.post_json(
            '/submissions',
            {
                'data': {
                    "tenderers": [test_docs_tenderer],
                    "frameworkID": self.framework_id,
                }
            }
        )
        self.submission_1_id = response.json["data"]["id"]
        self.submission_1_token = response.json["access"]["token"]

        local_tenderer = deepcopy(test_docs_tenderer)
        local_tenderer["identifier"]["id"] = "00137257"

        response = self.app.post_json(
            '/submissions',
            {
                'data': {
                    "tenderers": [local_tenderer],
                    "frameworkID": self.framework_id,
                }
            }
        )
        self.submission_2_id = response.json["data"]["id"]
        self.submission_2_token = response.json["access"]["token"]

        response = self.app.patch_json(
            f'/submissions/{self.submission_1_id}?acc_token={self.submission_1_token}',
            {'data': {"status": "active"}},
        )
        self.qualification_1_id = response.json["data"]["qualificationID"]

        response = self.app.patch_json(
            f'/submissions/{self.submission_2_id}?acc_token={self.submission_2_token}',
            {'data': {"status": "active"}},
        )
        self.qualification_2_id = response.json["data"]["qualificationID"]

        request_path = "/agreements"
        with open(TARGET_DIR + 'agreements-listing-0.http', 'wb') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = auth

        response = self.app.patch_json(
            f'/qualifications/{self.qualification_1_id}?acc_token={self.framework_token}',
            {'data': {"status": "active"}},
        )

        response = self.app.patch_json(
            f'/qualifications/{self.qualification_2_id}?acc_token={self.framework_token}',
            {'data': {"status": "active"}},
        )

        with open(TARGET_DIR + 'example-framework.http', 'wb') as self.app.file_obj:
            response = self.app.get(f'/frameworks/{self.framework_id}')
            self.assertEqual(response.status, '200 OK')

        self.agreement_id = response.json["data"]["agreementID"]

        with open(TARGET_DIR + 'agreement-view.http', 'wb') as self.app.file_obj:
            response = self.app.get(f'/agreements/{self.agreement_id}')
            self.assertEqual(response.status, '200 OK')

        contract_1_id = response.json['data']['contracts'][0]['id']
        contract_2_id = response.json['data']['contracts'][1]['id']

        with open(TARGET_DIR + 'milestone-list.http', 'wb') as self.app.file_obj:
            response = self.app.get(
                f"/agreements/{self.agreement_id}/contracts/{contract_1_id}/milestones",
            )
        contract_1_activation_milestone_id = response.json['data'][0]['id']

        ban_milestone = deepcopy(ban_milestone_data_with_documents)
        ban_milestone["documents"][0]["url"] = self.generate_docservice_url()

        with open(TARGET_DIR + 'milestone-ban-post.http', 'wb') as self.app.file_obj:
            response = self.app.post_json(
                f"/agreements/{self.agreement_id}"
                f"/contracts/{contract_1_id}"
                f"/milestones"
                f"?acc_token={self.framework_token}",
                {'data': ban_milestone},
            )
        contract_1_ban_milestone_id = response.json['data']['id']

        with open(TARGET_DIR + 'agreement-view-contract-suspended.http', 'wb') as self.app.file_obj:
            response = self.app.get(f'/agreements/{self.agreement_id}')
            self.assertEqual(response.status, '200 OK')

        self.assertEqual(response.json["data"]["contracts"][0]["status"], "suspended")

        self.tick(delta=timedelta(days=90))
        self.check_agreement_chronograph()

        with open(TARGET_DIR + 'agreement-view-contract-active.http', 'wb') as self.app.file_obj:
            response = self.app.get(f'/agreements/{self.agreement_id}')
            self.assertEqual(response.status, '200 OK')

        self.assertEqual(response.json["data"]["contracts"][0]["status"], "active")

        with open(TARGET_DIR + 'milestone-activation-patch.http', 'wb') as self.app.file_obj:
            response = self.app.patch_json(
                f"/agreements/{self.agreement_id}"
                f"/contracts/{contract_1_id}"
                f"/milestones/{contract_1_activation_milestone_id}"
                f"?acc_token={self.framework_token}",
                {'data': {"status": "met"}},
            )

        with open(TARGET_DIR + 'agreement-view-contract-terminated.http', 'wb') as self.app.file_obj:
            response = self.app.get(f'/agreements/{self.agreement_id}')
            self.assertEqual(response.status, '200 OK')

        self.assertEqual(response.json["data"]["contracts"][0]["status"], "terminated")

        self.tick(delta=timedelta(days=90))
        self.check_agreement_chronograph()

        with open(TARGET_DIR + 'agreement-view-terminated.http', 'wb') as self.app.file_obj:
            response = self.app.get(f'/agreements/{self.agreement_id}')
            self.assertEqual(response.status, '200 OK')

    def check_agreement_chronograph(self):
        with change_auth(self.app, ("Basic", ("chronograph", ""))):
            url = "/agreements/{}".format(self.agreement_id)
            data = {"data": {"id": self.agreement_id}}
            response = self.app.patch_json(url, data)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
