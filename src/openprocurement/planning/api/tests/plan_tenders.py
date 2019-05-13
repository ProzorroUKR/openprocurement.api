from openprocurement.planning.api.tests.base import BasePlanWebTest, test_plan_data
from openprocurement.tender.belowthreshold.tests.base import test_tender_data as below_tender_data
from openprocurement.tender.cfaua.tests.base import test_tender_w_lot_data as cfa_tender_data
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_data_eu as cd_eu_tender_data,
    test_tender_data_ua as cd_ua_tender_data,
    test_tender_stage2_data_ua as cd_stage2_data_ua,
    test_tender_stage2_data_eu as cd_stage2_data_eu,
)
from openprocurement.tender.esco.tests.base import test_tender_data as esco_tender_data
from openprocurement.tender.limited.tests.base import (
    test_tender_data as reporting_tender_data,
    test_tender_negotiation_data as negotiation_tender_data,
    test_tender_negotiation_quick_data as negotiation_quick_tender_data
)
from openprocurement.tender.openeu.tests.base import test_tender_data as openeu_tender_data
from openprocurement.tender.openua.tests.base import test_tender_data as openua_tender_data
from openprocurement.tender.openuadefense.tests.base import test_tender_data as defense_tender_data
from openprocurement.tender.cfaselectionua.tests.tender import tender_data as cfa_selection_tender_data
from openprocurement.api.tests.base import BaseTestApp, loadwsgiapp
from copy import deepcopy
import os.path
import pytest


@pytest.fixture(scope="session")
def singleton_app():
    app = BaseTestApp(
        loadwsgiapp(
            "config:tests.ini",
            relative_to=os.path.dirname(__file__)
        )
    )
    return app


@pytest.fixture(scope="function")
def app(singleton_app):
    singleton_app.authorization = None
    singleton_app.recreate_db()
    yield singleton_app
    singleton_app.drop_db()


@pytest.fixture(scope="function")
def plan(app):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json('/plans', {'data': deepcopy(test_plan_data)})
    return response.json


def test_get_plan_tenders_501(app, plan):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.get(
        '/plans/{}/tenders'.format(plan["data"]["id"]),
        status=501
    )
    assert response.json == {u'status': u'error',
                             u'errors': [{u'description': u'Not implemented',
                                          u'location': u'request',
                                          u'name': u'method'}]}


def test_plan_tenders_403(app, plan):
    app.authorization = ('Basic', ("broker", "broker"))
    app.post_json(
        '/plans/{}/tenders'.format(plan["data"]["id"]),
        {'data': {}},
        status=403
    )


def test_plan_tenders_404(app):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json(
        '/plans/{}/tenders'.format("a" * 32),
        {'data': {}},
        status=404
    )
    assert response.status == '404 Not Found'
    assert response.content_type == 'application/json'
    assert response.json == {
        u'status': u'error',
        u'errors': [{u'description': u'Not Found', u'location': u'url', u'name': u'plan_id'}]
    }


def test_plan_tenders_422(app, plan):
    app.authorization = ('Basic', ("broker", "broker"))
    app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': {}},
        status=422
    )


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
]
for n, e in enumerate(test_tenders):
    test_tenders[n] = deepcopy(e)


@pytest.mark.parametrize("tender_request_data", test_tenders)
def test_fail_validation_plan_tenders_creation(app, plan, tender_request_data):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': tender_request_data},
        status=422
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procuringEntity"
    plan_identifier = test_plan_data["procuringEntity"]["identifier"]
    tender_identifier = tender_request_data["procuringEntity"]["identifier"]
    assert errors[0]["description"] == "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
        plan_identifier["scheme"], plan_identifier["id"],
        tender_identifier["scheme"], tender_identifier["id"],
    )


@pytest.mark.parametrize("tender_request_data", test_tenders)
def test_success_plan_tenders_creation(app, plan, tender_request_data):
    plan_identifier = test_plan_data["procuringEntity"]["identifier"]
    tender_request_data["procuringEntity"]["identifier"]["id"] = plan_identifier["id"]
    tender_request_data["procuringEntity"]["identifier"]["scheme"] = plan_identifier["scheme"]

    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': tender_request_data}
    )
    assert response.status == '201 Created'

    tender_data = response.json["data"]
    assert tender_data["plan_id"] == plan["data"]["id"]
    assert tender_data["title"] == tender_request_data["title"]
    assert response.headers["Location"] == "http://localhost/api/2.5/tenders/{}".format(tender_data["id"])


@pytest.mark.parametrize("tender_request_data", test_tenders)
def test_fail_pass_plan_id(app, plan, tender_request_data):
    """
    plan_id cannot be set via /tenders endpoint
    """
    app.authorization = ('Basic', ("broker", "broker"))
    tender_data = dict(**tender_request_data)
    tender_data["plan_id"] = plan["data"]["id"]
    response = app.post_json(
        '/tenders',
        {'data': tender_request_data}
    )
    assert response.status == '201 Created'
    tender_data = response.json["data"]

    assert "plan_id" not in tender_data  # NOT in
    assert tender_data["title"] == tender_request_data["title"]


def test_fail_cfa_second_stage_creation(app, plan):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': cfa_selection_tender_data},
        status=422
    )
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error['name'] == 'procurementMethodType'
    assert error['description'].startswith(u"Should be one of the first stage values:")


@pytest.mark.parametrize("tender_request_data", [cd_stage2_data_ua, cd_stage2_data_eu])
def test_fail_cd_second_stage_creation(app, plan, tender_request_data):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': tender_request_data},
        status=403
    )
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error['name'] == 'accreditation'
    assert u"Broker Accreditation level does not permit tender creation" == error['description']
