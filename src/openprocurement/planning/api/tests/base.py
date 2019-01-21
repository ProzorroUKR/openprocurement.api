# -*- coding: utf-8 -*-
import unittest
import webtest
import os
from base64 import b64encode
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.api.constants import VERSION, SESSION
from requests.models import Response
from urllib import urlencode
from uuid import uuid4

now = datetime.now()
test_plan_data = {
        "tender": {
            "procurementMethod": u"open",
            "procurementMethodType": u"belowThreshold",
            "tenderPeriod": {
                "startDate": (now + timedelta(days=7)).isoformat()
            }
        },
        "items": [
            {
                "deliveryDate": {
                    "endDate": (now + timedelta(days=15)).isoformat()
                },
                "additionalClassifications": [
                    {
                        "scheme": u"ДКПП",
                        "id": u"01.11.92",
                        "description": u"Насіння гірчиці"
                    }
                ],
                "unit": {
                    "code": u"KGM",
                    "name": u"кг"
                },
                "classification": {
                    "scheme": u"ДК021",
                    "description": u"Mustard seeds",
                    "id": u"03111600-8"
                },
                "quantity": 1000,
                "description": u"Насіння гірчиці"
            },
            {
                "deliveryDate": {
                    "endDate": (now + timedelta(days=16)).isoformat()
                },
                "additionalClassifications": [
                    {
                        "scheme": u"ДКПП",
                        "id": u"01.11.95",
                        "description": u"Насіння соняшнику"
                    }
                ],
                "unit": {
                    "code": u"KGM",
                    "name": u"кг"
                },
                "classification": {
                    "scheme": u"ДК021",
                    "description": u"Sunflower seeds",
                    "id": u"03111300-5"
                },
                "quantity": 2000,
                "description": u"Насіння соняшнику"
            },
            {
                "deliveryDate": {
                    "endDate": (now + timedelta(days=17)).isoformat()
                },
                "additionalClassifications": [
                    {
                        "scheme": u"ДКПП",
                        "id": u"01.11.84",
                        "description": u"Насіння бавовнику"
                    }
                ],
                "unit": {
                    "code": u"KGM",
                    "name": u"кг"
                },
                "classification": {
                    "scheme": u"ДК021",
                    "description": u"Cotton seeds",
                    "id": u"03111400-6"
                },
                "quantity": 3000,
                "description": u"Насіння бавовнику"
            }
        ],
        "classification": {
            "scheme": u"ДК021",
            "description": u"Seeds",
            "id": u"03111000-2"
        },
        "additionalClassifications": [
            {
                "scheme": u"КЕКВ",
                "id": u"1",
                "description": u"-"
            }
        ],
        "procuringEntity": {
            "identifier": {
                "scheme": u"UA-EDR",
                "id": u"111983",
                "legalName": u"ДП Державне Управління Справами"
            },
            "name": u"ДУС"
        },
        "budget": {
            "project": {
                "name": u"proj_name",
                "id": u"123"
            },
            "amount": 10000,
            "amountNet": 12222,
            "currency": u"UAH",
            "id": u"12303111000-2",
            "description": u"budget_description",
            "period": {
                "startDate": datetime(year=now.year, month=1, day=1).isoformat(),
                "endDate": datetime(year=now.year, month=12, day=31).isoformat()
            }
        }
    }


class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseWebTest(unittest.TestCase):

    """Base Web Test to test openprocurement.planning.api.

    It setups the database before each test and delete it after.
    """

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini", relative_to=os.path.dirname(__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('token', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def tearDown(self):
        del self.couchdb_server[self.db.name]


class BasePlanWebTest(BaseWebTest):
    initial_data = test_plan_data
    docservice = False

    def setUp(self):
        super(BasePlanWebTest, self).setUp()
        self.create_plan()
        if self.docservice:
            self.setUpDS()

    def setUpDS(self):
        self.app.app.registry.docservice_url = 'http://localhost'
        test = self
        def request(method, url, **kwargs):
            response = Response()
            if method == 'POST' and '/upload' in url:
                url = test.generate_docservice_url()
                response.status_code = 200
                response.encoding = 'application/json'
                response._content = '{{"data":{{"url":"{url}","hash":"md5:{md5}","format":"application/msword","title":"name.doc"}},"get_url":"{url}"}}'.format(url=url, md5='0'*32)
                response.reason = '200 OK'
            return response

        self._srequest = SESSION.request
        SESSION.request = request

    def generate_docservice_url(self):
        uuid = uuid4().hex
        key = self.app.app.registry.docservice_key
        keyid = key.hex_vk()[:8]
        signature = b64encode(key.signature("{}\0{}".format(uuid, '0' * 32)))
        query = {'Signature': signature, 'KeyID': keyid}
        return "http://localhost/get/{}?{}".format(uuid, urlencode(query))

    def create_plan(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json('/plans', {'data': data})
        plan = response.json['data']
        self.plan_token = response.json['access']['token']
        self.plan_id = plan['id']

    def tearDownDS(self):
        SESSION.request = self._srequest

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.db[self.plan_id]
        super(BasePlanWebTest, self).tearDown()
