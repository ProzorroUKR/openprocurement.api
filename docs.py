# -*- coding: utf-8 -*-
import json
import os
from datetime import timedelta

from openprocurement.api.models import get_now
import openprocurement.contracting.api.tests.base as base_test
from openprocurement.api.tests.base import PrefixedRequestClass
from openprocurement.contracting.api.tests.base import BaseWebTest
from openprocurement.contracting.api.tests.base import test_contract_data
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
                            'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
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
                    self.file_obj.write(json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TenderResourceTest(BaseWebTest):
    initial_auth = ('Basic', ('databridge', ''))
    # ('Basic', ('broker', ''))
    initial_data = test_contract_data

    def setUp(self):
        self.app = DumpsTestAppwebtest(
                "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def test_docs(self):
        request_path = '/contracts'

        #### Exploring basic rules
        #

        with  open('docs/source/tutorial/contracts-listing.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')
            self.app.file_obj.write("\n")

        with  open('docs/source/tutorial/contract-post-attempt.http', 'w') as self.app.file_obj:
            response = self.app.post(request_path, 'data', status=415)
            self.assertEqual(response.status, '415 Unsupported Media Type')

        self.app.authorization = ('Basic', ('broker', ''))

        with open('docs/source/tutorial/contract-post-attempt-json.http', 'w') as self.app.file_obj:
            self.app.authorization = ('Basic', ('databridge', ''))
            response = self.app.post(
                    request_path, 'data', content_type='application/json', status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')

        #### Creating tender
        #

        with open('docs/source/tutorial/contract-post-attempt-json-data.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/contracts?opt_pretty=1', {"data": test_contract_data})
            self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('broker', ''))

        tender = response.json['data']
        owner_token = response.json['access']['token']


        with open('docs/source/tutorial/contract-json-data-view.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}'.format(tender['id']))
            self.assertEqual(response.status, '200 OK')

        with open('docs/source/tutorial/contract-listing-no-auth.http', 'w') as self.app.file_obj:
            self.app.authorization = None
            response = self.app.get(request_path)
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Modifying tender
        #

