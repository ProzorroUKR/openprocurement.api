# -*- coding: utf-8 -*-
import pytest
from uuid import uuid4
from copy import deepcopy
from openprocurement.api.tests.base import singleton_app, app
from openprocurement.planning.api.tests.base import test_plan_data
from openprocurement.tender.openua.tests.base import (
    test_tender_openua_config,
    test_tender_openua_data,
)


test_tender_openua_central_data = deepcopy(test_tender_openua_data)

test_plan_central_data = deepcopy(test_plan_data)
test_plan_central_data["procuringEntity"]["identifier"] = test_tender_openua_central_data["procuringEntity"]["identifier"]

test_tender_openua_central_data["status"] = "draft"
test_tender_openua_central_data["procuringEntity"]["kind"] = "central"
test_tender_openua_central_data["items"] = test_tender_openua_central_data["items"][:1]
test_tender_openua_central_data["items"][0]["classification"]["id"] = test_plan_central_data["items"][0]["classification"]["id"]
test_tender_openua_central_data["buyers"] = [{
    "id": uuid4().hex,
    "name": "name",
    "name_en": "name_en",
    "identifier": {
        "scheme": "UA-EDR",
        "id": "111983",
        "legalName": "ДП Державне Управління Справами"
    },
}]
test_tender_openua_central_data["items"][0]["relatedBuyer"] = test_tender_openua_central_data["buyers"][0]["id"]


def test_get_tender_plans_404(app):
    response = app.get("/tenders/{}/plans".format("a" * 32), status=404)
    assert response.json == {"status": "error", "errors": [
        {"location": "url", "name": "tender_id", "description": "Not Found"}]}


@pytest.fixture(scope="function")
def tender(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_tender_openua_central_data)
    response = app.post_json("/tenders", dict(data=test_data, config=test_tender_openua_config))
    assert response.status == "201 Created"
    return response.json


@pytest.fixture(scope="function")
def plan(app):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": deepcopy(test_plan_central_data)})
    return response.json


def test_get_tender_plans_empty(app, tender):
    response = app.get("/tenders/{}/plans".format(tender["data"]["id"]))
    assert response.status == "200 OK"
    assert response.json == {"data": []}


def test_post_tender_plan_403(app, tender):
    app.post_json("/tenders/{}/plans".format(tender["data"]["id"]), status=403)


def test_post_tender_plan_empty(app, tender):
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {},
        status=422
    )
    assert response.json == {"status": "error", "errors": [
        {"location": "body", "name": "data", "description": "Data not available"}]}


def test_post_tender_plan_data_empty(app, tender):
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {}},
        status=422
    )
    assert response.json == {'status': 'error', 'errors': [
        {'description': ['This field is required.'], 'location': 'body', 'name': 'id'}]}


def test_post_tender_plan_404(app, tender):
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": tender["data"]["id"]}},
        status=404
    )
    assert response.json == {'status': 'error', 'errors': [
        {'description': 'Not Found', 'location': 'url', 'name': 'plan_id'}]}


def test_post_tender_plan_success(app, tender, plan):
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
    )
    assert response.json["data"] == [{'id': plan["data"]["id"]}]

    response = app.get("/tenders/{}".format(tender["data"]["id"]))
    assert response.json["data"]["dateModified"] > tender["data"]["dateModified"]

    response = app.get("/plans/{}".format(plan["data"]["id"]))
    assert response.json["data"]["tender_id"] == tender["data"]["id"]
    assert response.json["data"]["dateModified"] > plan["data"]["dateModified"]

    # second plan
    response = app.post_json("/plans", {"data": deepcopy(test_plan_central_data)})
    another_plan = response.json

    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": another_plan["data"]["id"]}},
    )
    assert response.json["data"] == [{'id': plan["data"]["id"]},
                                     {'id': another_plan["data"]["id"]}]


def test_fail_not_draft(app, plan):
    app.authorization = ("Basic", ("broker", "broker"))

    test_data = deepcopy(test_tender_openua_central_data)
    del test_data["status"]
    response = app.post_json("/tenders", dict(data=test_data, config=test_tender_openua_config))
    assert response.status == "201 Created"
    app.set_initial_status(response.json, "active.tendering")
    tender = response.json

    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
        status=403
    )
    assert response.json == {"status": "error", "errors": [
        {"location": "body", "name": "data", "description": "Only allowed in draft tender status"}]}


def test_fail_non_central(app, plan):
    app.authorization = ("Basic", ("broker", "broker"))

    test_data = deepcopy(test_tender_openua_central_data)
    test_data["procuringEntity"]["kind"] = "general"
    response = app.post_json("/tenders", dict(data=test_data, config=test_tender_openua_config))
    assert response.status == "201 Created"
    tender = response.json

    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
        status=403
    )
    assert response.json == {"status": "error", "errors": [
        {"location": "body", "name": "data", "description": "Only allowed for procurementEntity.kind = 'central'"}]}


def test_fail_duplicate(app, tender, plan):
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
    )
    assert response.status == "200 OK"

    # the same
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
        status=422
    )
    assert response.json == {'status': 'error', 'errors': [
        {'description': "Can't update plan in 'complete' status", 'location': 'body', 'name': 'status'}]}

    # what if plan hasn't been updated for an unknown reason
    plan_obj = app.app.registry.mongodb.plans.get(plan["data"]["id"])
    del plan_obj["tender_id"]
    plan_obj["status"] = "scheduled"
    app.app.registry.mongodb.save_data(app.app.registry.mongodb.plans.collection, plan_obj)

    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
        status=422
    )
    assert response.json == {'status': 'error', 'errors': [
        {'description': ['The list should not contain duplicates'], 'location': 'body', 'name': 'plans'}]}
    # in this case the plan might be completed manually


def test_fail_saving_plan(app, tender, plan):
    plan_obj = app.app.registry.mongodb.plans.get(plan["data"]["id"])
    plan_obj["status"] = "will cause a data validation error"
    app.app.registry.mongodb.save_data(app.app.registry.mongodb.plans.collection, plan_obj)

    # got an error
    response = app.post_json(
        "/tenders/{}/plans?acc_token={}".format(tender["data"]["id"], tender["access"]["token"]),
        {"data": {"id": plan["data"]["id"]}},
        status=422
    )
    assert response.json == {"status": "error", "errors": [
        {"location": "body", "name": "status", "description": [
            "Value must be one of ['draft', 'scheduled', 'cancelled', 'complete']."]}]}

    # check that the tender hasn't been changed
    tender_obj = app.app.registry.mongodb.tenders.get(tender["data"]["id"])
    assert tender_obj.get("plans") is None
