# -*- coding: utf-8 -*-
import json
import os

import openprocurement.planning.api.tests.base as base_test
from openprocurement.planning.api.tests.base import PrefixedRequestClass, BasePlanWebTest
from openprocurement.planning.api.tests.base import test_plan_data
from webtest import TestApp


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                        '\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('Response: %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(
                        json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class PlanResourceTest(BasePlanWebTest):
    initial_data = test_plan_data

    def setUp(self):
        self.app = DumpsTestAppwebtest(
            "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def test_docs(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # empty plans listing
        response = self.app.get('/plans')
        self.assertEqual(response.json['data'], [])

        # create plan
        with open('docs/source/tutorial/create-plan.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/plans?opt_pretty=1', {"data": test_plan_data})
            self.assertEqual(response.status, '201 Created')

        plan = response.json['data']
        plan_id = self.plan_id = response.json['data']['id']
        owner_token = response.json['access']['token']

        with open('docs/source/tutorial/example_plan.http', 'w') as self.app.file_obj:
            response = self.app.get('/plans/{}'.format(plan_id))

        with open('docs/source/tutorial/plan-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/plans')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/patch-plan-procuringEntity-name.http', 'w') as self.app.file_obj:
            response = self.app.patch_json('/plans/{}?acc_token={}'.format(plan['id'], owner_token), {'data':
                {"items": [
                    {
                        "description": "Насіння овочевих культур",
                        "classification": {
                            "scheme": "ДК021",
                            "description": "Vegetable seeds",
                            "id": "03111700-9"
                        },
                        "additionalClassifications": [
                            {
                                "scheme": "ДКПП",
                                "id": "01.13.6",
                                "description": "Насіння овочевих культур"
                            }
                        ],
                        "deliveryDate": {
                            "endDate": "2016-06-01T23:06:30.023018+03:00"
                        },
                        "unit": {
                            "code": "KGM",
                            "name": "кг"
                        },
                        "quantity": 5000
                    }
                ]
                }
            })

        with open('docs/source/tutorial/plan-listing-after-patch.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get('/plans')
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")
