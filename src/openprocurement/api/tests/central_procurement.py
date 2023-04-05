# -*- coding: utf-8 -*-
from uuid import uuid4

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_data as below_tender_data,
    test_tender_config as below_tender_config,
)
from openprocurement.tender.cfaua.tests.base import test_tender_w_lot_data as cfa_tender_data
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_data_eu as cd_eu_tender_data,
    test_tender_data_ua as cd_ua_tender_data,
)
from openprocurement.tender.esco.tests.base import test_tender_data as esco_tender_data
from openprocurement.tender.limited.tests.base import (
    test_tender_data as reporting_tender_data,
    test_tender_negotiation_data as negotiation_tender_data,
    test_tender_negotiation_quick_data as negotiation_quick_tender_data,
    test_tender_config as limited_tender_config,
)
from openprocurement.tender.openeu.tests.base import test_tender_data as openeu_tender_data
from openprocurement.tender.openua.tests.base import test_tender_data as openua_tender_data
from openprocurement.tender.openuadefense.tests.base import test_tender_data as defense_tender_data
from openprocurement.tender.cfaselectionua.tests.tender import tender_data as cfa_selection_tender_data
from openprocurement.tender.simpledefense.tests.tender import test_tender_data as simple_defense_tender_data

from openprocurement.api.tests.base import BaseTestApp, loadwsgiapp
from openprocurement.api.constants import RELEASE_SIMPLE_DEFENSE_FROM
from openprocurement.api.utils import get_now
from copy import deepcopy
import pytest
import os


test_tenders = [
    (below_tender_data, below_tender_config),
    (cfa_tender_data, below_tender_config),
    (cd_eu_tender_data, below_tender_config),
    (cd_ua_tender_data, below_tender_config),
    (esco_tender_data, below_tender_config),
    (reporting_tender_data, limited_tender_config),
    (negotiation_tender_data, limited_tender_config),
    (negotiation_quick_tender_data, limited_tender_config),
    (openeu_tender_data, below_tender_config),
    (openua_tender_data, below_tender_config),
    (cfa_selection_tender_data, below_tender_config),
]


if get_now() > RELEASE_SIMPLE_DEFENSE_FROM:
    test_tenders.append((simple_defense_tender_data, below_tender_config))
else:
    test_tenders.append((defense_tender_data, below_tender_config))


@pytest.fixture(scope="session")
def singleton_app():
    app = BaseTestApp(loadwsgiapp("config:tests.ini", relative_to=os.path.dirname(__file__)))
    app.app.registry.docservice_url = "http://localhost"
    return app


@pytest.fixture(scope="function")
def app(singleton_app):
    singleton_app.authorization = None
    yield singleton_app


@pytest.mark.parametrize("request_tender_data, request_tender_config", test_tenders)
def test_buyers_not_required(app, request_tender_data, request_tender_config):
    test_data = deepcopy(request_tender_data)
    test_data.pop("buyers", None)
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/tenders", {"data": test_data, "config": request_tender_config})
    assert response.status == "201 Created"


@pytest.mark.parametrize("request_tender_data, request_tender_config", test_tenders)
def test_set_buyers(app, request_tender_data, request_tender_config):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(request_tender_data)
    test_data["buyers"] = [
        {
            "id": uuid4().hex,
            "name": "Державне управління справами",
            "identifier": {
                "scheme": "UA-EDR",
                "id": "00037256",
                "uri": "http://www.dus.gov.ua/"
            },
        }
    ]
    for item in test_data["items"]:
        item["relatedBuyer"] = test_data["buyers"][0]["id"]
    response = app.post_json("/tenders", {"data": test_data, "config": request_tender_config})
    assert response.status == "201 Created"
    assert len(response.json["data"]["buyers"]) == 1


@pytest.mark.parametrize("request_tender_data, request_tender_config", test_tenders)
def test_central_kind_buyers_required(app, request_tender_data, request_tender_config):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(request_tender_data)
    test_data["procuringEntity"]["kind"] = "central"

    response = app.post_json("/tenders", {"data": test_data, "config": request_tender_config}, status=422)
    assert response.json == {"status": "error", "errors": [
        {"location": "body", "name": "buyers", "description": ["This field is required."]}
    ]}
