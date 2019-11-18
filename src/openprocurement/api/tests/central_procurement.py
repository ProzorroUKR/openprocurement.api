# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_tender_data as below_tender_data
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
)
from openprocurement.tender.openeu.tests.base import test_tender_data as openeu_tender_data
from openprocurement.tender.openua.tests.base import test_tender_data as openua_tender_data
from openprocurement.tender.openuadefense.tests.base import test_tender_data as defense_tender_data
from openprocurement.tender.cfaselectionua.tests.tender import tender_data as cfa_selection_tender_data

from openprocurement.api.tests.base import BaseTestApp, loadwsgiapp
from copy import deepcopy
import pytest
import os


test_tenders = [
    below_tender_data,
    cfa_tender_data,
    cd_eu_tender_data,
    cd_ua_tender_data,
    esco_tender_data,
    reporting_tender_data,
    negotiation_tender_data,
    negotiation_quick_tender_data,
    openeu_tender_data,
    openua_tender_data,
    defense_tender_data,
    cfa_selection_tender_data,
]


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


@pytest.mark.parametrize("request_tender_data", test_tenders)
def test_buyers_not_required(app, request_tender_data):
    test_data = deepcopy(request_tender_data)
    test_data.pop("buyers", None)

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/tenders", {"data": test_data})
    assert response.status == "201 Created"


@pytest.mark.parametrize("request_tender_data", test_tenders)
def test_set_buyers(app, request_tender_data):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(request_tender_data)
    test_data["buyers"] = [
        {
            "name": u"Державне управління справами",
            "identifier": {
                "scheme": u"UA-EDR",
                "id": u"00037256",
                "uri": u"http://www.dus.gov.ua/"
            },
        }
    ]

    response = app.post_json("/tenders", {"data": test_data})
    assert response.status == "201 Created"
    assert len(response.json["data"]["buyers"]) == 1


@pytest.mark.parametrize("request_tender_data", test_tenders)
def test_central_kind_buyers_required(app, request_tender_data):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(request_tender_data)
    test_data["procuringEntity"]["kind"] = "central"

    response = app.post_json("/tenders", {"data": test_data}, status=422)
    assert response.json == {"status": "error", "errors": [
        {"location": "body", "name": "buyers", "description": ["This field is required."]}
    ]}
