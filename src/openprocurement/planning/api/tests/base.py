# -*- coding: utf-8 -*-
import os
import pytest
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.tender.core.tests.base import BaseWebTest as BaseCoreWebTest
from openprocurement.api.tests.base import BaseTestApp, loadwsgiapp, BaseWebTest
from uuid import uuid4
from base64 import b64encode
from six.moves.urllib_parse import urlencode


now = datetime.now()
test_plan_data = {
    "tender": {
        "procurementMethod": u"open",
        "procurementMethodType": u"belowThreshold",
        "tenderPeriod": {"startDate": (now + timedelta(days=7)).isoformat()},
    },
    "items": [
        {
            "deliveryDate": {"endDate": (now + timedelta(days=15)).isoformat()},
            "additionalClassifications": [{"scheme": u"ДКПП", "id": u"01.11.92", "description": u"Насіння гірчиці"}],
            "unit": {"code": u"KGM", "name": u"кг"},
            "classification": {"scheme": u"ДК021", "description": u"Mustard seeds", "id": u"03111600-8"},
            "quantity": 1000,
            "description": u"Насіння гірчиці",
        },
        {
            "deliveryDate": {"endDate": (now + timedelta(days=16)).isoformat()},
            "additionalClassifications": [{"scheme": u"ДКПП", "id": u"01.11.95", "description": u"Насіння соняшнику"}],
            "unit": {"code": u"KGM", "name": u"кг"},
            "classification": {"scheme": u"ДК021", "description": u"Sunflower seeds", "id": u"03111300-5"},
            "quantity": 2000,
            "description": u"Насіння соняшнику",
        },
        {
            "deliveryDate": {"endDate": (now + timedelta(days=17)).isoformat()},
            "additionalClassifications": [{"scheme": u"ДКПП", "id": u"01.11.84", "description": u"Насіння бавовнику"}],
            "unit": {"code": u"KGM", "name": u"кг"},
            "classification": {"scheme": u"ДК021", "description": u"Cotton seeds", "id": u"03111400-6"},
            "quantity": 3000,
            "description": u"Насіння бавовнику",
        },
    ],
    "classification": {"scheme": u"ДК021", "description": u"Seeds", "id": u"03111000-2"},
    "additionalClassifications": [{"scheme": u"КЕКВ", "id": u"1", "description": u"-"}],
    "procuringEntity": {
        "identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
        "name": u"ДУС",
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "kind": "general",
    },
    "buyers": [
        {
            "identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
            "name": u"ДУС",
            "address": {
                "countryName": "Україна",
                "postalCode": "01220",
                "region": "м. Київ",
                "locality": "м. Київ",
                "streetAddress": "вул. Банкова, 11, корпус 1",
            },
            "kind": "general",
        }
    ],
    "budget": {
        "project": {"name": u"proj_name", "id": u"123"},
        "amount": 10000,
        "amountNet": 12222,
        "currency": u"UAH",
        "id": u"12303111000-2",
        "description": u"budget_description",
        "period": {
            "startDate": datetime(year=now.year, month=1, day=1).isoformat(),
            "endDate": datetime(year=now.year, month=12, day=31).isoformat(),
        },
        "breakdown": [
            {
                "title": u"other",
                "description": u"Breakdown other description.",
                "value": {"amount": 1500, "currency": u"UAH"},
            }
        ],
    },
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BasePlanTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))


class BasePlanWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_plan_data
    docservice = False

    def setUp(self):
        super(BasePlanWebTest, self).setUp()
        self.create_plan()

    def create_plan(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json("/plans", {"data": data})
        plan = response.json["data"]
        self.plan_token = response.json["access"]["token"]
        self.plan_id = plan["id"]

    def tearDown(self):
        del self.db[self.plan_id]
        super(BasePlanWebTest, self).tearDown()


@pytest.fixture(scope="session")
def singleton_app():
    app = BaseTestApp(loadwsgiapp("config:tests.ini", relative_to=os.path.dirname(__file__)))
    app.app.registry.docservice_url = "http://localhost"
    return app


@pytest.fixture(scope="function")
def app(singleton_app):
    singleton_app.authorization = None
    singleton_app.recreate_db()
    yield singleton_app
    singleton_app.drop_db()


@pytest.fixture(scope="function")
def plan(app):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": deepcopy(test_plan_data)})
    return response.json


def generate_docservice_url(app):
    uuid = uuid4().hex
    key = app.app.registry.docservice_key
    keyid = key.hex_vk()[:8]
    signature = b64encode(key.signature("{}\0{}".format(uuid, "0" * 32)))
    query = {"Signature": signature, "KeyID": keyid}
    return "{}/get/{}?{}".format(app.app.registry.docservice_url, uuid, urlencode(query))
