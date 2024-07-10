# pylint: disable=unused-import
from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

import pytest

from openprocurement.api.utils import get_now
from openprocurement.planning.api.tests.base import (
    app,
    generate_docservice_url,
    singleton_app,
    test_plan_data,
)


def test_plan_default_status(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)

    test_data.pop("status", None)
    response = app.post_json("/plans", {"data": test_data})
    assert response.json["data"].get("status") == "scheduled"

    test_data["status"] = None
    response = app.post_json("/plans", {"data": test_data})
    assert response.json["data"].get("status") == "scheduled"

    response = app.get("/plans")
    assert response.status == "200 OK"
    assert len(response.json["data"]) == 2


@pytest.mark.parametrize("mode", ["real", "test", "_all_"])
def test_plan_draft_status(app, mode):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)

    if mode != "real":
        test_data["mode"] = "test"
    test_data["status"] = "draft"

    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == "draft"

    response = app.get("/plans?mode={}".format(mode))
    assert response.status == "200 OK"
    assert len(response.json["data"]) == 0

    response = app.get("/plans?feed=changes&mode={}".format(mode))
    assert response.status == "200 OK"
    assert len(response.json["data"]) == 0


@pytest.mark.parametrize("initial_status", ["scheduled", None])
def test_fail_update_back_to_draft(app, initial_status):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)

    test_data["status"] = initial_status
    response = app.post_json("/plans", {"data": test_data})
    assert response.json["data"].get("status") == "scheduled"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    if initial_status is None:
        plan = app.app.registry.mongodb.plans.get(plan_id)
        del plan["status"]
        app.app.registry.mongodb.plans.save(plan)

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": "draft"}}, status=422
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Plan status can not be changed back to 'draft'",
                "location": "body",
                "name": "status",
            }
        ],
    }


def test_update_status_invalid(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)

    test_data["status"] = "draft"
    response = app.post_json("/plans", {"data": test_data})
    assert response.json["data"].get("status") == "draft"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": "invalid"}}, status=422
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "location": "body",
                "name": "status",
                "description": ["Value must be one of ['draft', 'scheduled', 'cancelled', 'complete']."],
            }
        ],
    }

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": "cancelled"}}, status=422
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {"description": ["An active cancellation object is required"], "location": "body", "name": "status"}
        ],
    }


@pytest.mark.parametrize("status", ["scheduled", "complete"])
@pytest.mark.parametrize("mode", ["real", "test", "_all_"])
def test_plan_update_draft(app, mode, status):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    if mode != "real":
        test_data["mode"] = "test"
    test_data["status"] = "draft"
    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == "draft"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    response = app.patch_json("/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": status}})
    assert response.status == "200 OK"
    assert response.json["data"].get("status") == status

    response = app.get("/plans?mode={}".format(mode))
    assert response.status == "200 OK"
    assert len(response.json["data"]) == 1
    assert response.json["data"][0]["id"] == plan_id

    response = app.get("/plans?feed=changes&mode={}".format(mode))
    assert response.status == "200 OK"
    assert len(response.json["data"]) == 1
    assert response.json["data"][0]["id"] == plan_id


def test_plan_update_scheduled_to_complete(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = "scheduled"

    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == "scheduled"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    response = app.patch_json("/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": "complete"}})
    assert response.status == "200 OK"
    assert response.json["data"].get("status") == "complete"


@pytest.mark.parametrize("initial_status", ["draft", "scheduled"])
def test_cancel_plan_2_steps(app, initial_status):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = initial_status
    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == initial_status
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    cancellation = {
        "reason": "Because",
        "status": "pending",
    }

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token),
        {"data": {"cancellation": cancellation}},
    )
    assert response.status == "200 OK"
    assert response.json["data"]["cancellation"]["status"] == "pending"
    assert response.json["data"].get("status") == initial_status
    create_time = response.json["data"]["cancellation"]["date"]

    cancellation["status"] = "active"

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token),
        {"data": {"cancellation": cancellation}},
    )
    assert response.status == "200 OK"
    assert response.json["data"]["cancellation"]["status"] == "active"
    assert response.json["data"]["cancellation"]["date"] > create_time
    assert response.json["data"]["status"] == "cancelled"

    get_response = app.get("/plans/{}".format(plan_id))
    assert get_response.json["data"]["cancellation"]["date"] == response.json["data"]["cancellation"]["date"]


def test_cancel_plan_1_step(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = "scheduled"
    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == "scheduled"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    cancellation = {
        "reason": "",
        "status": "active",
    }

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token),
        {"data": {"cancellation": cancellation}},
        status=422,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {"location": "body", "name": "cancellation", "description": {"reason": ["String value is too short."]}}
        ],
    }

    cancellation = {
        "reason": "Because",
        "status": "active",
    }

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token),
        {"data": {"cancellation": cancellation}},
    )
    assert response.status == "200 OK"
    assert response.json["data"]["cancellation"]["status"] == "active"
    assert response.json["data"]["status"] == "cancelled"

    plan = app.app.registry.mongodb.plans.get(plan_id)
    assert {c["path"] for c in plan["revisions"][-1]["changes"]} == {"/cancellation", "/status"}


@pytest.mark.parametrize("replaced_status", ["draft", "scheduled", "complete"])
def test_create_cancelled(app, replaced_status):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = replaced_status  # this will be replaced by "switch_status" serializable
    test_data["cancellation"] = {"reason": "Because it's possible", "status": "active"}
    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == "cancelled"


def test_cancel_compatibility_completed_plan(app):
    """
    well I don't know if it's an appropriate case. it's probably not
    """
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"

    plan = response.json["data"]
    acc_token = response.json["access"]["token"]

    obj = app.app.registry.mongodb.plans.get(plan["id"])
    del obj["status"]
    obj["tender_id"] = "a" * 32
    app.app.registry.mongodb.save_data(app.app.registry.mongodb.plans.collection, obj)

    response = app.get("/plans/{}".format(plan["id"]))
    assert response.json["data"]["status"] == "complete"  # complete !

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"cancellation": {"reason": "Because it's possible", "status": "active"}}},
    )
    assert response.status == "200 OK"
    assert response.json["data"]["status"] == "cancelled"  # cancelled !


@pytest.mark.parametrize("status", ["cancelled", "complete"])
def test_fail_update_complete_or_cancelled_plan(app, status):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["documents"] = [
        {
            "title": "укр.doc",
            "url": generate_docservice_url(app),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    test_data["status"] = status
    if status == "cancelled":
        test_data["cancellation"] = {"reason": "Because", "status": "active"}

    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"].get("status") == status
    plan_id = response.json["data"]["id"]
    doc_id = response.json["data"]["documents"][0]["id"]
    acc_token = response.json["access"]["token"]

    # patch is allowed, but only "rationale" is allowed
    classification = deepcopy(test_data["classification"])
    classification["description"] = "bla"
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token),
        {"data": {"classification": classification, "rationale": {"description": "hello, 123#"}}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Can't update classification in {} status".format(status),
                "location": "body",
                "name": "data",
            }
        ],
    }

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token),
        {"data": {"rationale": {"description": "hello, 123#"}}},
    )
    assert response.json["data"]["classification"]["description"] != "bla"
    assert response.json["data"]["rationale"]["description"] == "hello, 123#"

    #  docs
    response = app.post_json(
        "/plans/{}/documents?acc_token={}".format(plan_id, acc_token),
        {
            "data": {
                "title": "укр.doc",
                "url": generate_docservice_url(app),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Can't update plan in '{}' status".format(status),
                "location": "body",
                "name": "status",
            }
        ],
    }

    response = app.put_json(
        "/plans/{}/documents/{}?acc_token={}".format(plan_id, doc_id, acc_token),
        {
            "data": {
                "title": "укр.doc",
                "url": generate_docservice_url(app),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Can't update plan in '{}' status".format(status),
                "location": "body",
                "name": "status",
            }
        ],
    }

    response = app.patch_json(
        "/plans/{}/documents/{}?acc_token={}".format(plan_id, doc_id, acc_token),
        {"data": {"title": "whatever.doc"}},
        status=422,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Can't update plan in '{}' status".format(status),
                "location": "body",
                "name": "status",
            }
        ],
    }

    # tender creation
    response = app.post_json("/plans/{}/tenders".format(plan_id), {"data": {}}, status=422)
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Can't create tender in '{}' plan status".format(status),
                "location": "body",
                "name": "status",
            }
        ],
    }


@pytest.mark.parametrize(
    "value",
    [
        "aboveThresholdUA",
        "aboveThresholdUA.defense",
        "simple.defense",
        "aboveThresholdEU",
        "esco",
        "competitiveDialogueUA",
        "competitiveDialogueEU",
        "closeFrameworkAgreementUA",
    ],
)
def test_fail_complete_manually(app, value):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = "scheduled"
    test_data["tender"]["procurementMethodType"] = value
    if value == "aboveThresholdUA.defense":
        patch_date = get_now() + timedelta(days=1)
    else:
        patch_date = get_now() - timedelta(days=1)

    if value in ("aboveThresholdUA.defense", "simple.defense"):
        with patch("openprocurement.planning.api.procedure.state.plan.RELEASE_SIMPLE_DEFENSE_FROM", patch_date):
            response = app.post_json("/plans", {"data": test_data}, status=403)
        assert response.status == "403 Forbidden"
        assert response.json["errors"] == [
            {
                "description": (
                    "procuringEntity with general kind cannot publish this type of procedure. Procurement "
                    "method types allowed for this kind: centralizedProcurement, belowThreshold, aboveThreshold, "
                    "aboveThresholdUA, aboveThresholdEU, competitiveDialogueUA, competitiveDialogueEU, esco, "
                    "closeFrameworkAgreementUA, priceQuotation, reporting, negotiation, negotiation.quick."
                ),
                'location': 'body',
                'name': 'kind',
            }
        ]
        test_data["procuringEntity"]["kind"] = "defense"

    with patch("openprocurement.planning.api.procedure.state.plan.RELEASE_SIMPLE_DEFENSE_FROM", patch_date):
        response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"]["status"] == "scheduled"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": "complete"}}, status=422
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "location": "body",
                "name": "status",
                "description": ["Can't complete plan with '{}' tender.procurementMethodType".format(value)],
            }
        ],
    }


@pytest.mark.parametrize("value", [("open", "belowThreshold"), ("limited", "reporting")])
def test_success_complete_manually(app, value):
    procurement_method, procurement_method_type = value
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = "scheduled"
    test_data["tender"]["procurementMethod"] = procurement_method
    test_data["tender"]["procurementMethodType"] = procurement_method_type
    response = app.post_json("/plans", {"data": test_data})
    assert response.status == "201 Created"
    assert response.json["data"]["status"] == "scheduled"
    plan_id = response.json["data"]["id"]
    acc_token = response.json["access"]["token"]

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, acc_token), {"data": {"status": "complete"}}, status=200
    )
    assert response.json["data"]["status"] == "complete"
