# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from uuid import uuid4
from copy import deepcopy

from openprocurement.api.utils import get_now
from openprocurement.planning.api.tests.base import BasePlanWebTest
from openprocurement.planning.api.constants import (
    MILESTONE_APPROVAL_TITLE,
    MILESTONE_APPROVAL_DESCRIPTION,
)
from openprocurement.tender.openua.tests.base import test_tender_openua_config
from tests.base.data import (
    test_docs_plan_data,
    test_docs_tender_openua,
    test_docs_tender_openeu,
)
from tests.base.constants import DOCS_URL
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)

TARGET_DIR = 'docs/source/centralized-procurements/http/'

test_plan_data = deepcopy(test_docs_plan_data)
test_tender_eu_data = deepcopy(test_docs_tender_openeu)
test_tender_ua_data = deepcopy(test_docs_tender_openua)

central_entity = {
    "identifier": {
        "scheme": "UA-EDR",
        "id": "111111",
        "legalName": "ДП Центральний закупівельний орган №1"
    },
    "name": "ЦЗО №1",
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 1",
    },
    "kind": "central"
}


class PlanResourceTest(BasePlanWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_plan_data
    docservice_url = DOCS_URL

    def setUp(self):
        super(PlanResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(PlanResourceTest, self).tearDown()

    def create_plan(self):
        pass

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty plans listing
        response = self.app.get('/plans')
        self.assertEqual(response.json['data'], [])

        # create plan
        test_plan_data['status'] = "draft"
        test_plan_data['items'] = test_plan_data['items'][:1]
        test_plan_data["buyers"] = [deepcopy(test_plan_data["procuringEntity"])]  # just to be sure
        test_plan_data["procuringEntity"] = central_entity

        with open(TARGET_DIR + 'create-plan.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/plans?opt_pretty=1',
                {'data': test_plan_data}
            )

        self.assertEqual(response.status, '201 Created')

        _plan = response.json['data']
        self.plan_id = _plan["id"]
        owner_token = response.json['access']['token']

        self.tick()

        with open(TARGET_DIR + 'patch-plan-status-scheduled.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(_plan['id'], owner_token),
                {'data': {"status": "scheduled"}}
            )
        self.assertEqual(response.json["data"]["status"], "scheduled")

        self.tick()

        with open(TARGET_DIR + 'post-plan-milestone.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/plans/{}/milestones'.format(_plan['id']),
                {
                    'data': {
                        "title": MILESTONE_APPROVAL_TITLE,
                        "description": MILESTONE_APPROVAL_DESCRIPTION,
                        "type": "approval",
                        "author": central_entity,
                        "dueDate": (get_now() + timedelta(seconds=1)).isoformat(),
                    }
                }
            )
        self.assertEqual(response.json["data"]["status"], "scheduled")
        milestone = response.json["data"]
        milestone_token = response.json["access"]["token"]

        self.tick()

        with open(TARGET_DIR + 'patch-plan-milestone.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}/milestones/{}?acc_token={}'.format(
                    _plan['id'], milestone["id"], milestone_token
                ),
                {
                    'data': {
                        "status": "met",
                        "description": "Доповнений опис відповіді",
                        "dueDate": (get_now() + timedelta(seconds=1)).isoformat(),
                    }
                }
            )
        self.assertEqual(response.status_code, 200)

        self.tick()

        with open(TARGET_DIR + 'post-plan-milestone-document.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/plans/{}/milestones/{}/documents?acc_token={}'.format(
                    _plan["id"], milestone["id"], milestone_token
                ),
                {
                    "data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }
                }
            )
        self.assertEqual(response.status_code, 201)

        # tender creation
        procuring_entity = deepcopy(test_plan_data["procuringEntity"])
        procuring_entity.update(
            contactPoint=dict(name="Довідкова", telephone="+0440000000"),
            address=test_tender_ua_data["procuringEntity"]["address"],
            kind="central",
        )
        test_tender_ua_data["procuringEntity"] = procuring_entity

        buyer1 = deepcopy(test_plan_data["buyers"][0])
        buyer1["id"] = uuid4().hex

        buyer2 = deepcopy(test_plan_data["buyers"][0])
        buyer2["id"] = uuid4().hex
        buyer2["identifier"]["id"] = "222983"

        test_tender_ua_data["buyers"] = [buyer1, buyer2]
        test_tender_ua_data["items"] = deepcopy(test_docs_plan_data["items"])
        test_tender_ua_data["items"][0]["relatedBuyer"] = buyer1["id"]  # assign buyers
        test_tender_ua_data["items"][1]["relatedBuyer"] = buyer1["id"]
        test_tender_ua_data["items"][2]["relatedBuyer"] = buyer2["id"]

        test_tender_ua_data["status"] = "draft"

        self.tick()

        with open(TARGET_DIR + 'create-tender.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders',
                {'data': test_tender_ua_data, 'config': test_tender_openua_config}
            )
        self.assertEqual(response.status, '201 Created')
        tender = response.json

        # attaching plans to the tender

        self.tick()

        with open(TARGET_DIR + 'post-tender-plans.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/plans?acc_token={}'.format(
                    tender["data"]["id"],
                    tender["access"]["token"]
                ),
                {"data": {"id": _plan['id']}}
            )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'plan-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/plans/{}'.format(_plan['id']))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender["data"]["id"]))
        self.assertEqual(response.status, '200 OK')
