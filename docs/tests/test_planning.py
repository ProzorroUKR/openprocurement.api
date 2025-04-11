import os
from copy import deepcopy
from datetime import timedelta

from tests.base.constants import DOCS_URL
from tests.base.data import (
    test_docs_plan_data,
    test_docs_tender_below,
    test_docs_tender_openeu,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.planning.api.tests.base import BasePlanWebTest
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_config

TARGET_DIR = 'docs/source/planning/tutorial/'

test_docs_plan_data = deepcopy(test_docs_plan_data)
test_docs_tender_openeu = deepcopy(test_docs_tender_openeu)
test_docs_tender_below = deepcopy(test_docs_tender_below)


class PlanResourceTest(BasePlanWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_docs_plan_data
    docservice_url = DOCS_URL

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

    def create_plan(self):
        pass

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty plans listing
        response = self.app.get('/plans')
        self.assertEqual(response.json['data'], [])

        # create plan
        test_docs_plan_data['status'] = "draft"

        test_breakdown = deepcopy(test_docs_plan_data['budget']['breakdown'])
        del test_docs_plan_data['budget']['breakdown']

        with open(TARGET_DIR + 'create-plan.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/plans?opt_pretty=1', {'data': test_docs_plan_data})
            self.assertEqual(response.status, '201 Created')

        plan = response.json['data']
        self.plan_id = plan["id"]
        owner_token = response.json['access']['token']

        with open(TARGET_DIR + 'patch-plan-status-scheduled.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token), {'data': {"status": "scheduled"}}
            )
            self.assertEqual(response.json["data"]["status"], "scheduled")

        with open(TARGET_DIR + 'plan-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/plans')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'patch-plan-procuringEntity-name.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token),
                {
                    'data': {
                        "items": [
                            {
                                "description": "Насіння овочевих культур",
                                "classification": {
                                    "scheme": "ДК021",
                                    "description": "Vegetable seeds",
                                    "id": "03111700-9",
                                },
                                "additionalClassifications": [
                                    {"scheme": "ДКПП", "id": "01.13.6", "description": "Насіння овочевих культур"}
                                ],
                                "deliveryDate": {"endDate": "2016-06-01T23:06:30.023018+03:00"},
                                "unit": {"code": "KGM", "name": "кг"},
                                "quantity": 5000,
                            }
                        ]
                    }
                },
            )

        with open(TARGET_DIR + 'plan-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/plans')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        # tender creation

        self.app.authorization = ('Basic', ('broker', ''))

        with open(TARGET_DIR + 'tender-from-plan-validation.http', 'w') as self.app.file_obj:
            self.app.post_json('/plans/{}/tenders'.format(plan['id']), {'data': test_docs_tender_openeu}, status=422)

        test_docs_tender_below["items"] = test_docs_plan_data["items"]
        test_docs_tender_below["procuringEntity"]["identifier"] = test_docs_plan_data["procuringEntity"]["identifier"]
        test_docs_tender_below["title"] = "Насіння"
        test_docs_tender_below["status"] = "draft"

        with open(TARGET_DIR + 'tender-from-plan-breakdown.http', 'w') as self.app.file_obj:
            self.app.post_json(
                '/plans/{}/tenders'.format(plan['id']),
                {'data': test_docs_tender_below, 'config': test_tender_below_config},
                status=422,
            )

        budget = deepcopy(test_docs_plan_data['budget'])
        budget['breakdown'] = test_breakdown
        budget["project"] = {"id": "532ba4bc-e1a7-4334-8d8e-59646d5dcee6", "name": "Project name"}
        with open(TARGET_DIR + 'patch-plan-budget-project-name-invalid.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token),
                {'data': {"budget": budget}},
                status=422,
            )

        budget["project"] = {
            "id": "95f87658-ffa5-472e-89ee-6e9417aa8cbd",
            "name": "1.1. Набрання чинності законодавчими змінами щодо реформи оплати праці в державній службі",
            "name_en": "1.1. Entry into force of the legislative changes to the civil service remuneration reform",
        }
        with open(TARGET_DIR + 'patch-plan-breakdown.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token), {'data': {"budget": budget}}
            )

        budget["breakdown"][0]["title"] = "state"
        with open(
            TARGET_DIR + 'patch-plan-budget-breakdown-classifications-state-invalid.http', 'w'
        ) as self.app.file_obj:
            self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token),
                {'data': {"budget": budget}},
                status=422,
            )

        budget["breakdown"][0]["classification"] = {
            "scheme": "КПК-2023",
            "id": "3505000",
            "description": "Державна аудиторська служба України",
        }
        with open(TARGET_DIR + 'patch-plan-budget-breakdown-classifications-state.http', 'w') as self.app.file_obj:
            self.app.patch_json('/plans/{}?acc_token={}'.format(plan['id'], owner_token), {'data': {"budget": budget}})

        budget["breakdown"][0]["title"] = "local"
        del budget["breakdown"][0]["classification"]
        with open(
            TARGET_DIR + 'patch-plan-budget-breakdown-classifications-local-invalid.http', 'w'
        ) as self.app.file_obj:
            self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token),
                {'data': {"budget": budget}},
                status=422,
            )

        budget["breakdown"][0]["classification"] = {
            "scheme": "ТКПКМБ",
            "id": "2170",
            "description": "Будівництво закладів охорони здоров’я",
        }

        with open(
            TARGET_DIR + 'patch-plan-budget-breakdown-classifications-local-address-invalid.http', 'w'
        ) as self.app.file_obj:
            self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan['id'], owner_token),
                {'data': {"budget": budget}},
                status=422,
            )

        budget["breakdown"][0]["addressDetails"] = {
            "countryName": "Україна",
            "code": {
                "scheme": "КАТОТТГ",
                "id": "UA01020030010043419",
                "description": "Ароматне",
            },
        }
        with open(TARGET_DIR + 'patch-plan-budget-breakdown-classifications-local.http', 'w') as self.app.file_obj:
            self.app.patch_json('/plans/{}?acc_token={}'.format(plan['id'], owner_token), {'data': {"budget": budget}})

        with open(TARGET_DIR + 'tender-from-plan.http', 'w') as self.app.file_obj:
            self.app.post_json(
                '/plans/{}/tenders'.format(plan['id']),
                {'data': test_docs_tender_below, 'config': test_tender_below_config},
            )

        # readonly

        with open(TARGET_DIR + 'tender-from-plan-readonly.http', 'w') as self.app.file_obj:
            self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan["id"], owner_token),
                {
                    'data': {
                        'procuringEntity': {
                            "identifier": {
                                "scheme": "UA-EDR",
                                "id": "111983",
                                "legalName": "ДП Державне Управління Справами",
                            },
                            "name": "ДУС",
                        }
                    }
                },
                status=422,
            )

        with open(TARGET_DIR + 'get-complete-plan.http', 'w') as self.app.file_obj:
            response = self.app.get('/plans/{}'.format(plan['id']))
        self.assertEqual(response.json["data"]["status"], "complete")

        # update complete plan
        self.tick(delta=timedelta(days=1, hours=1, seconds=33))
        rationale = 'Змістовне пояснення необхідності закупівлі'
        with open(TARGET_DIR + 'complete-plan-rationale.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan["id"], owner_token),
                {'data': {'rationale': {"description": rationale}}},
            )
        self.assertEqual(response.json["data"]["rationale"]["description"], rationale)

        # rationale history
        with open(TARGET_DIR + 'plan-rationale-history.http', 'w') as self.app.file_obj:
            self.app.get(f"/history/plans/{plan['id']}?opt_fields=rationale")

        # tender manually completion
        response = self.app.post_json('/plans', {'data': test_docs_plan_data})
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + 'complete-plan-manually.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(response.json['data']['id'], response.json['access']['token']),
                {'data': {"status": "complete"}},
            )
            self.assertEqual(response.json["data"]["status"], "complete")

        # tender cancellation
        test_docs_plan_data["status"] = "scheduled"
        response = self.app.post_json('/plans', {'data': test_docs_plan_data})
        self.assertEqual(response.status, '201 Created')

        plan_id = response.json['data']['id']
        acc_token = response.json['access']['token']

        with open(TARGET_DIR + 'plan-cancellation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan_id, acc_token),
                {
                    'data': {
                        "cancellation": {
                            "reason": "Підстава для скасування",
                            "reason_en": "Reason of the cancellation",
                        }
                    }
                },
            )
        self.assertEqual(response.json["data"]["status"], "scheduled")

        with open(TARGET_DIR + 'plan-cancellation-activation.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/plans/{}?acc_token={}'.format(plan_id, acc_token),
                {
                    'data': {
                        "cancellation": {
                            "reason": "Підстава для скасування",
                            "status": "active",
                        }
                    }
                },
            )
        self.assertEqual(response.json["data"]["status"], "cancelled")
