# -*- coding: utf-8 -*-
import os
import pytest
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.tender.core.tests.base import BaseWebTest as BaseCoreWebTest
from openprocurement.api.tests.base import BaseTestApp, loadwsgiapp
from uuid import uuid4
from base64 import b64encode
from urllib.parse import urlencode
from nacl.encoding import HexEncoder


now = datetime.now()
test_plan_data = {
    "tender": {
        "procurementMethod": "open",
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": {"startDate": (now + timedelta(days=7)).isoformat()},
    },
    "items": [
        {
            "deliveryDate": {"endDate": (now + timedelta(days=15)).isoformat()},
            "additionalClassifications": [{"scheme": "ДКПП", "id": "01.11.92", "description": "Насіння гірчиці"}],
            "unit": {"code": "KGM", "name": "кг"},
            "classification": {"scheme": "ДК021", "description": "Mustard seeds", "id": "03111600-8"},
            "quantity": 1000,
            "description": "Насіння гірчиці",
        },
        {
            "deliveryDate": {"endDate": (now + timedelta(days=16)).isoformat()},
            "additionalClassifications": [{"scheme": "ДКПП", "id": "01.11.95", "description": "Насіння соняшнику"}],
            "unit": {"code": "KGM", "name": "кг"},
            "classification": {"scheme": "ДК021", "description": "Sunflower seeds", "id": "03111300-5"},
            "quantity": 2000,
            "description": "Насіння соняшнику",
        },
        {
            "deliveryDate": {"endDate": (now + timedelta(days=17)).isoformat()},
            "additionalClassifications": [{"scheme": "ДКПП", "id": "01.11.84", "description": "Насіння бавовнику"}],
            "unit": {"code": "KGM", "name": "кг"},
            "classification": {"scheme": "ДК021", "description": "Cotton seeds", "id": "03111400-6"},
            "quantity": 3000,
            "description": "Насіння бавовнику",
        },
    ],
    "classification": {"scheme": "ДК021", "description": "Seeds", "id": "03111000-2"},
    "additionalClassifications": [{"scheme": "КЕКВ", "id": "1", "description": "-"}],
    "procuringEntity": {
        "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
        "name": "ДУС",
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
            "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
            "name": "ДУС",
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
        "project": {"name": "proj_name", "id": "123"},
        "amount": 10000,
        "amountNet": 12222,
        "currency": "UAH",
        "id": "12303111000-2",
        "description": "budget_description",
        "period": {
            "startDate": datetime(year=now.year, month=1, day=1).isoformat(),
            "endDate": datetime(year=now.year, month=12, day=31).isoformat(),
        },
        "breakdown": [
            {
                "title": "other",
                "description": "Breakdown other description.",
                "value": {"amount": 1500, "currency": "UAH"},
            }
        ],
    },
}


class BasePlanTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))
    docservice = True


class BasePlanWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_plan_data
    docservice = True

    def setUp(self):
        super(BasePlanWebTest, self).setUp()
        self.create_plan()

    def create_plan(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json("/plans", {"data": data})
        plan = response.json["data"]
        self.plan_token = response.json["access"]["token"]
        self.plan_id = plan["id"]


@pytest.fixture(scope="session")
def singleton_app():
    app = BaseTestApp(loadwsgiapp("config:tests.ini", relative_to=os.path.dirname(__file__)))
    app.app.registry.docservice_url = "http://localhost"
    return app


@pytest.fixture(scope="function")
def app(singleton_app):
    singleton_app.authorization = None
    singleton_app.app.registry.mongodb.plans.flush()
    yield singleton_app
    singleton_app.app.registry.mongodb.plans.flush()


@pytest.fixture(scope="function")
def plan(app):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": deepcopy(test_plan_data)})
    return response.json


def generate_docservice_url(app, doc_hash=None):
    uuid = uuid4().hex
    doc_hash = doc_hash or '0' * 32
    registry = app.app.registry
    signer = registry.docservice_key
    keyid = signer.verify_key.encode(encoder=HexEncoder)[:8].decode()
    msg = "{}\0{}".format(uuid, doc_hash).encode()
    signature = b64encode(signer.sign(msg).signature)
    query = {"Signature": signature, "KeyID": keyid}
    return "{}/get/{}?{}".format(app.app.registry.docservice_url, uuid, urlencode(query))
