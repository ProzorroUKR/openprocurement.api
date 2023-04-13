# -*- coding: utf-8 -*-
import os
import pytest
from uuid import uuid4
from copy import deepcopy
from openprocurement.api.tests.base import BaseTestApp, loadwsgiapp
from openprocurement.api.constants import RELEASE_SIMPLE_DEFENSE_FROM
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_data,
    test_tender_below_config,
)
from openprocurement.tender.openeu.tests.base import (
    test_tender_openeu_data,
    test_tender_openeu_config,
)
from openprocurement.tender.openua.tests.base import (
    test_tender_openua_data,
    test_tender_openua_config,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cdeu_data,
    test_tender_cdua_data,
    test_tender_cdeu_config,
    test_tender_cdua_config,
)
from openprocurement.tender.esco.tests.base import (
    test_tender_esco_data,
    test_tender_esco_config,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_reporting_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    test_tender_reporting_config,
    test_tender_negotiation_config,
    test_tender_negotiation_quick_config,
)
from openprocurement.tender.openuadefense.tests.base import (
    test_tender_openuadefense_data,
    test_tender_openuadefense_config,
)
from openprocurement.tender.simpledefense.tests.base import (
    test_tender_simpledefense_data,
    test_tender_simpledefense_config,
)
from openprocurement.tender.cfaua.tests.base import (
    test_tender_cfaua_with_lots_data,
    test_tender_cfaua_config,
)
from openprocurement.tender.cfaselectionua.tests.tender import test_tender_cfaselectionua_data
from openprocurement.tender.cfaselectionua.tests.base import test_tender_cfaselectionua_config

test_tenders = [
    (test_tender_below_data, test_tender_below_config),
    (test_tender_cfaua_with_lots_data, test_tender_cfaua_config),
    (test_tender_cfaselectionua_data, test_tender_cfaselectionua_config),
    (test_tender_cdeu_data, test_tender_cdeu_config),
    (test_tender_cdua_data, test_tender_cdua_config),
    (test_tender_esco_data, test_tender_esco_config),
    (test_tender_reporting_data, test_tender_reporting_config),
    (test_tender_negotiation_data, test_tender_negotiation_config),
    (test_tender_negotiation_quick_data, test_tender_negotiation_quick_config),
    (test_tender_openeu_data, test_tender_openeu_config),
    (test_tender_openua_data, test_tender_openua_config),
]


if get_now() > RELEASE_SIMPLE_DEFENSE_FROM:
    test_tenders.append((test_tender_simpledefense_data, test_tender_simpledefense_config))
else:
    test_tenders.append((test_tender_openuadefense_data, test_tender_openuadefense_config))


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
