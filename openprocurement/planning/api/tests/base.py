# -*- coding: utf-8 -*-
import unittest
import webtest
import os
from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from openprocurement.api.utils import VERSION


now = datetime.now()
test_plan_data =  {
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
                    "scheme": u"CPV",
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
                    "scheme": u"CPV",
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
                    "scheme": u"CPV",
                    "description": u"Cotton seeds",
                    "id": u"03111400-6"
                },
                "quantity": 3000,
                "description": u"Насіння бавовнику"
            }
        ],
        "classification": {
            "scheme": u"CPV",
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
            "description": u"budget_description"
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

