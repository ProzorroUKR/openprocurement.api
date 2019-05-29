# -*- coding: utf-8 -*-
from openprocurement.planning.api.tests.base import BasePlanWebTest, test_plan_data
from openprocurement.planning.api.constants import PROCEDURES
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


def test_get_plan_tenders_405(app, plan):
    app.authorization = ('Basic', ("broker", "broker"))
    response = app.get(
        '/plans/{}/tenders'.format(plan["data"]["id"]),
        status=405
    )
    assert response.json == {u'status': u'error',
                             u'errors': [{u'description': u'Method not allowed',
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


test_below_tender_data = deepcopy(below_tender_data)
test_below_tender_data["procuringEntity"]["identifier"] = test_plan_data["procuringEntity"]["identifier"]
test_below_tender_data["items"] = test_below_tender_data["items"][:1]
test_below_tender_data["items"][0]["classification"] = test_plan_data["items"][0]["classification"]


def test_fail_identifier_id_validation(app):
    app.authorization = ('Basic', ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["procuringEntity"]["identifier"]["id"] = "911"
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': test_below_tender_data},
        status=422
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procuringEntity"
    plan_identifier = plan["data"]["procuringEntity"]["identifier"]
    tender_identifier = test_below_tender_data["procuringEntity"]["identifier"]
    assert errors[0]["description"] == "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
        plan_identifier["scheme"], plan_identifier["id"],
        tender_identifier["scheme"], tender_identifier["id"],
    )


def test_fail_identifier_scheme_validation(app):
    app.authorization = ('Basic', ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["procuringEntity"]["identifier"]["scheme"] = "AE-DCCI"
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': test_below_tender_data},
        status=422
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procuringEntity"
    plan_identifier = plan["data"]["procuringEntity"]["identifier"]
    tender_identifier = test_below_tender_data["procuringEntity"]["identifier"]
    assert errors[0]["description"] == "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
        plan_identifier["scheme"], plan_identifier["id"],
        tender_identifier["scheme"], tender_identifier["id"],
    )


def test_fail_procurement_method_type_validation(app):
    app.authorization = ('Basic', ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["tender"]["procurementMethodType"] = "aboveThresholdUA"
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': test_below_tender_data},
        status=422
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procurementMethodType"
    assert errors[0]["description"] == "procurementMethodType doesn't match: aboveThresholdUA != belowThreshold"


def test_success_classification_id(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {
        "scheme": u"ДК021",
        "description": "Antiperspirants",
        "id": "33711120-4",
    }
    del request_plan_data["items"]

    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Make-up preparations",
        "id": "33711200-9",
    }
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': request_tender_data}
    )
    assert response.status == '201 Created'


def test_fail_classification_id(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {
        "scheme": u"ДК021",
        "description": "Personal care products",
        "id": "33700000-7",
    }
    del request_plan_data["items"]

    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Antiperspirants",
        "id": "33711120-4",
    }
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': request_tender_data},
        status=422
    )
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error['name'] == 'items[0].classification.id'
    assert error['description'] == "Plan classification.id 33700000-7 and item's 33711120-4 " \
                                   "should be of the same group 3370"


def test_success_classification_id_336(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {
        "scheme": u"ДК021",
        "description": "Insulin",
        "id": "33615100-5",
    }
    del request_plan_data["items"]

    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"] = request_tender_data["items"][:1]
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Medicinal products for dermatology",
        "id": "33631000-2"
    }
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': request_tender_data}
    )
    assert response.status == '201 Created'


def test_fail_classification_id_336(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {
        "scheme": u"ДК021",
        "description": "Pharmaceutical products",
        "id": "33600000-6",
    }
    del request_plan_data["items"]

    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json('/plans', {'data': request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"] = request_tender_data["items"][:1]
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Makeup kits",
        "id": "33711420-7",
    }
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': request_tender_data},
        status=422
    )
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error['name'] == 'items[0].classification.id'
    assert error['description'] == "Plan classification.id 33600000-6 and item's 33711420-7 " \
                                   "should be of the same group 336"


def create_plan_for_tender(app, data):
    request_plan_data = deepcopy(test_plan_data)

    request_plan_data["tender"]["procurementMethodType"] = data["procurementMethodType"]
    procedure_values = {procedure: k for k, v in PROCEDURES.items() for procedure in v}
    request_plan_data["tender"]["procurementMethod"] = procedure_values[data["procurementMethodType"]]

    request_plan_data["procuringEntity"]["identifier"]["id"] = data["procuringEntity"]["identifier"]["id"]
    request_plan_data["procuringEntity"]["identifier"]["scheme"] = data["procuringEntity"]["identifier"]["scheme"]

    request_plan_data["classification"] = data["items"][0]["classification"]
    request_plan_data["items"][0]["classification"] = request_plan_data["classification"]
    request_plan_data["items"][1]["classification"] = request_plan_data["classification"]
    request_plan_data["items"][2]["classification"] = request_plan_data["classification"]

    app.authorization = ('Basic', ("broker", "broker"))
    response = app.post_json('/plans', {'data': request_plan_data})
    return response.json


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


@pytest.mark.parametrize("tender_request_data", test_tenders)
def test_success_plan_tenders_creation(app, tender_request_data):
    app.authorization = ('Basic', ("broker", "broker"))
    plan = create_plan_for_tender(app, tender_request_data)

    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': tender_request_data}
    )
    assert response.status == '201 Created'

    tender_data = response.json["data"]
    assert tender_data["plan_id"] == plan["data"]["id"]
    assert tender_data["title"] == tender_request_data["title"]
    assert response.headers["Location"] == "http://localhost/api/2.5/tenders/{}".format(tender_data["id"])

    # get plan
    response = app.get('/plans/{}'.format(plan["data"]["id"]))
    assert response.json["data"]["tender_id"] == tender_data["id"]

    # add another tender
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': tender_request_data},
        status=409
    )
    error_data = response.json["errors"]
    assert len(error_data) == 1
    error = error_data[0]
    assert error['location'] == 'url'
    assert error['name'] == 'id'
    assert error['description'] == 'This plan has already got a tender'


def test_tender_creation_modified_date(app):
    app.authorization = ('Basic', ("broker", "broker"))
    plan = create_plan_for_tender(app, below_tender_data)

    # get feed last links
    response = app.get('/plans')
    date_feed = response.json
    assert len(date_feed["data"]) == 1
    assert date_feed["data"][0]["id"] == plan["data"]["id"]
    assert date_feed["data"][0]["dateModified"] == plan["data"]["dateModified"]

    response = app.get('/plans?feed=changes')
    change_feed = response.json
    assert len(change_feed["data"]) == 1
    assert change_feed["data"][0]["id"] == plan["data"]["id"]
    assert change_feed["data"][0]["dateModified"] == plan["data"]["dateModified"]

    # post tender
    response = app.post_json(
        '/plans/{}/tenders?acc_token={}'.format(plan["data"]["id"], plan["access"]["token"]),
        {'data': below_tender_data}
    )
    assert response.status == '201 Created'

    # get updated plan
    response = app.get('/plans/{}'.format(plan["data"]["id"]))
    updated_plan = response.json
    assert plan["data"]["dateModified"] == updated_plan["data"]["dateModified"]

    # check feeds: date feed is empty, but changes feed shows plan with the same dateModified
    response = app.get("/" + date_feed["next_page"]["path"].split("/")[-1])
    new_date_feed = response.json
    assert new_date_feed != date_feed
    assert len(new_date_feed["data"]) == 0
    assert new_date_feed["next_page"]["offset"] == date_feed["next_page"]["offset"]

    response = app.get('/plans?feed=changes&offset={}'.format(change_feed["next_page"]["offset"]))
    new_change_feed = response.json
    assert len(new_change_feed["data"]) == 1
    assert new_change_feed["data"][0]["id"] == plan["data"]["id"]
    assert new_change_feed["data"][0]["dateModified"] == plan["data"]["dateModified"]
    assert new_change_feed["next_page"]["offset"] != change_feed["next_page"]["offset"]


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
