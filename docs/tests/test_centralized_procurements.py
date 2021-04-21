# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from freezegun import freeze_time
from openprocurement.planning.api.tests.base import BasePlanWebTest
from openprocurement.planning.api.constants import MILESTONE_APPROVAL_TITLE, MILESTONE_APPROVAL_DESCRIPTION
from tests.base.data import plan
from openprocurement.tender.belowthreshold.tests.base import test_tender_data
from tests.base.data import tender_openeu
from tests.base.constants import DOCS_URL
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

TARGET_DIR = 'docs/source/centralized-procurements/http/'

test_plan_data = deepcopy(plan)
tender_openeu = deepcopy(tender_openeu)
test_tender_data = deepcopy(test_tender_data)

central_entity = {
    "identifier": {
        "scheme": "UA-EDR",
        "id": "111111",
        "legalName": "ДП Центральний закупівельний орган №1"
    },
    "name": "ЦЗО №1"
}


class PlanResourceTest(BasePlanWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_plan_data
    docservice = True
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
        test_plan_data['tender'].update({"tenderPeriod": {"startDate": "2019-11-01T01:00:00+03:00"}})
        test_plan_data['items'][0].update({"deliveryDate": {"endDate": "2019-11-09T01:00:00+03:00"}})
        test_plan_data['items'] = test_plan_data['items'][:1]

        test_plan_data["buyers"] = [deepcopy(test_plan_data["procuringEntity"])]  # just to be sure

        test_plan_data["procuringEntity"] = central_entity

        with freeze_time("2019-05-02 01:00:00"):
            with open(TARGET_DIR + 'create-plan.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/plans?opt_pretty=1',
                    {'data': test_plan_data})
        self.assertEqual(response.status, '201 Created')

        plan = response.json['data']
        self.plan_id = plan["id"]
        owner_token = response.json['access']['token']

        with freeze_time("2019-05-02 01:01:00"):
            with open(TARGET_DIR + 'patch-plan-status-scheduled.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/plans/{}?acc_token={}'.format(plan['id'], owner_token),
                    {'data': {"status": "scheduled"}}
                )
        self.assertEqual(response.json["data"]["status"], "scheduled")

        with freeze_time("2019-05-02 02:00:00"):
            with open(TARGET_DIR + 'post-plan-milestone.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/plans/{}/milestones'.format(plan['id']),
                    {'data': {
                        "title": MILESTONE_APPROVAL_TITLE,
                        "description": MILESTONE_APPROVAL_DESCRIPTION,
                        "type": "approval",
                        "author": central_entity,
                        "dueDate": "2019-05-15T13:00:00.000000+02:00",
                    }}
                )
        self.assertEqual(response.json["data"]["status"], "scheduled")
        milestone = response.json["data"]
        milestone_token = response.json["access"]["token"]

        with freeze_time("2019-05-02 03:00:00"):
            with open(TARGET_DIR + 'patch-plan-milestone.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/plans/{}/milestones/{}?acc_token={}'.format(
                        plan['id'], milestone["id"], milestone_token
                    ),
                    {'data': {
                        "status": "met",
                        "description": "Доповнений опис відповіді",
                        "dueDate": "2019-05-30T18:00:00.000000+02:00",
                    }}
                )
        self.assertEqual(response.status_code, 200)

        with freeze_time("2019-05-02 03:00:00"):
            with open(TARGET_DIR + 'post-plan-milestone-document.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/plans/{}/milestones/{}/documents?acc_token={}'.format(
                        plan["id"], milestone["id"], milestone_token
                    ),
                    {"data": {
                        "title": "Notice.pdf",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "application/pdf",
                    }}
                )
        self.assertEqual(response.status_code, 201)

        # tender creation
        procuring_entity = deepcopy(test_plan_data["procuringEntity"])
        procuring_entity.update(
            contactPoint=dict(name="Довідкова", telephone="+0440000000"),
            address=test_tender_data["procuringEntity"]["address"],
            kind="central",
        )
        test_tender_data["tenderPeriod"] = dict(
            startDate=test_plan_data["tender"]["tenderPeriod"]["startDate"],
            endDate="2019-11-11T01:00:00+03:00"
        )
        test_tender_data["enquiryPeriod"] = dict(
            startDate="2019-10-01T01:00:00+03:00",
            endDate="2019-10-30T01:00:00+03:00",
        )
        test_tender_data["procuringEntity"] = procuring_entity
        test_tender_data["buyers"] = test_plan_data["buyers"]
        test_tender_data["items"] = test_plan_data["items"]
        test_tender_data["status"] = "draft"

        with freeze_time("2019-05-12 09:00:00"):
            with open(TARGET_DIR + 'create-tender.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/tenders',
                    {'data': test_tender_data}
                )
        self.assertEqual(response.status, '201 Created')
        tender = response.json

        # attaching plans to the tender
        with freeze_time("2019-05-12 09:01:00"):
            with open(TARGET_DIR + 'post-tender-plans.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/tenders/{}/plans?acc_token={}'.format(
                        tender["data"]["id"],
                        tender["access"]["token"]
                    ),
                    {"data": {"id": plan['id']}}
                )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'plan-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/plans/{}'.format(plan['id']))
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'tender-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender["data"]["id"]))
        self.assertEqual(response.status, '200 OK')

