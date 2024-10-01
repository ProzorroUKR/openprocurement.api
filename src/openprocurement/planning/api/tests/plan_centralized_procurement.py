# pylint: disable=unused-import
from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.planning.api.constants import (
    MILESTONE_APPROVAL_DESCRIPTION,
    MILESTONE_APPROVAL_TITLE,
)
from openprocurement.planning.api.procedure.models.milestone import Milestone
from openprocurement.planning.api.tests.base import (
    app,
    generate_docservice_url,
    singleton_app,
    test_plan_data,
)

milestone_author = {
    "id": "1" * 32,
    "identifier": {"scheme": "UA-EDR", "id": "11111", "legalName": "ЦЗО 1"},
    "name": "ЦЗО 1",
}

central_procuring_entity = {
    "id": "2" * 32,
    "identifier": {"scheme": "UA-EDR", "id": "11111", "legalName": "ЦЗО 1"},
    "name": "ЦЗО 1",
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "kind": "general",
}


def test_milestone_data(app):
    test_milestone = {
        "title": MILESTONE_APPROVAL_TITLE,
        "type": Milestone.TYPE_APPROVAL,
        "author": milestone_author,
        "dueDate": datetime.now().isoformat(),
        "documents": [
            {
                "title": "name.doc",
                "url": generate_docservice_url(app),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        ],
    }
    return test_milestone


@pytest.fixture(scope="function")
def centralized_plan(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["tender"]["procurementMethod"] = ""
    test_data["tender"]["procurementMethodType"] = "centralizedProcurement"
    test_data["procuringEntity"] = central_procuring_entity
    response = app.post_json("/plans", {"data": test_data})
    return response.json["data"], response.json["access"]["token"]


def test_fail_create_plan_with_milestone(app):
    app.authorization = ("Basic", ("broker", "broker"))
    test_data = deepcopy(test_plan_data)
    test_data["status"] = "draft"
    test_data["milestones"] = [
        {
            "title": MILESTONE_APPROVAL_TITLE,
            "type": Milestone.TYPE_APPROVAL,
            "author": milestone_author,
            "dueDate": "2001-10-30T11:15:26.641038+03:00",
        }
    ]
    response = app.post_json("/plans", {"data": test_data}, status=422)
    assert response.json["errors"] == [{"location": "body", "name": "milestones", "description": "Rogue field"}]


def test_fail_post_milestone_author(app, centralized_plan):
    """
    milestone can only be posted if author equals plan.procuringEntity
    """
    plan, access_token = centralized_plan

    app.authorization = ("Basic", ("broker", "broker"))
    data = test_milestone_data(app)
    data["author"] = {"identifier": {"scheme": "UA-EDR", "id": "222222", "legalName": "ЦЗО 2"}, "name": "ЦЗО 2"}
    response = app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": data}, status=422)
    assert response.json == {
        "status": "error",
        "errors": [{"description": "Should match plan.procuringEntity", "location": "body", "name": "author"}],
    }


def test_post_milestone_author_validate_identifier(app, centralized_plan):
    """
    milestone can only be posted if author equals plan.procuringEntity
    """
    plan, access_token = centralized_plan

    app.authorization = ("Basic", ("broker", "broker"))
    data = test_milestone_data(app)
    data["author"]["name"] = "ЦЗО 2"
    app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": data}, status=201)


@pytest.mark.parametrize("test_status", [Milestone.STATUS_MET, Milestone.STATUS_NOT_MET, Milestone.STATUS_INVALID])
def test_fail_post_milestone_status(app, centralized_plan, test_status):
    """
    milestone can only be posted in scheduled status
    """
    plan, access_token = centralized_plan

    app.authorization = ("Basic", ("broker", "broker"))
    data = test_milestone_data(app)
    data["status"] = test_status
    response = app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": data}, status=422)
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Cannot create milestone with status: {}".format(test_status),
                "location": "body",
                "name": "status",
            }
        ],
    }


def test_post_milestone(app, centralized_plan):
    plan, access_token = centralized_plan

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": test_milestone_data(app)})
    assert response.status_code == 201
    milestone = response.json["data"]
    assert set(milestone.keys()) == {
        "status",
        "description",
        "title",
        "author",
        "id",
        "owner",
        "type",
        "dateModified",
        "dueDate",
        "documents",
    }
    assert milestone["description"] == MILESTONE_APPROVAL_DESCRIPTION
    assert milestone["status"] == Milestone.STATUS_SCHEDULED
    date_modified = parse_date(milestone["dateModified"])
    assert get_now() - date_modified < timedelta(seconds=1)
    assert "documents" in milestone
    assert "access" in response.json
    assert "token" in response.json["access"]

    response = app.get("/plans/{}".format(plan["id"]))
    assert response.json["data"]["dateModified"] == milestone["dateModified"]

    response = app.get("/plans/{}/milestones/{}".format(plan["id"], milestone["id"]))
    assert response.json["data"] == milestone


@pytest.fixture(scope="function")
def centralized_milestone(app, centralized_plan):
    plan, access_token = centralized_plan
    response = app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": test_milestone_data(app)})
    assert response.status_code == 201
    result = {
        "milestone": {"data": response.json["data"], "token": response.json["access"]["token"]},
        "plan": {"data": plan, "token": access_token},
    }
    return result


@pytest.mark.parametrize("test_status", [Milestone.STATUS_MET, Milestone.STATUS_SCHEDULED])
def test_fail_post_another_milestone(app, centralized_milestone, test_status):
    """
    broker can't post another milestone with the same author
    till the first milestone in scheduled or met statuses
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]

    # set milestone status
    if test_status != milestone["status"]:
        plan_source = app.app.registry.mongodb.plans.get(plan["id"])
        plan_source["milestones"][0]["status"] = test_status
        app.app.registry.mongodb.plans.save(plan_source)

    response = app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": test_milestone_data(app)}, status=422)
    assert response.json == {
        'status': 'error',
        'errors': [
            {'description': 'An active milestone already exists for this author', 'location': 'body', 'name': 'author'}
        ],
    }


@pytest.mark.parametrize("test_status", [Milestone.STATUS_NOT_MET, Milestone.STATUS_INVALID])
def test_success_post_another_milestone(app, centralized_milestone, test_status):
    """
    broker can post another milestone with the same author
    if the first milestone is invalid or notMet
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]

    # set milestone status
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["milestones"][0]["status"] = test_status
    app.app.registry.mongodb.plans.save(plan_source)

    response = app.post_json("/plans/{}/milestones".format(plan["id"]), {"data": test_milestone_data(app)}, status=201)
    assert response.json["data"]["id"] != milestone["id"]
    assert response.json["data"]["author"] == milestone["author"]
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    assert len(plan_source["milestones"]) == 2


def test_forbidden_patch_milestone(app, centralized_milestone):
    """
    plan owner or just broker can't patch milestone
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]

    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], plan_token),
        {"data": {"description": "What", "dueDate": "2001-10-30T11:15:26.641038+03:00"}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [{"location": "url", "name": "permission", "description": "Forbidden"}],
    }


@pytest.mark.parametrize("test_status", [Milestone.STATUS_NOT_MET, Milestone.STATUS_INVALID])
def test_fail_patch_due_date(app, centralized_milestone, test_status):
    """
    milestone owner can't patch dueDate if status != scheduled
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    # set milestone status
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["milestones"][0]["status"] = test_status
    app.app.registry.mongodb.plans.save(plan_source)

    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": {"dueDate": "2001-10-30T11:15:26.641038+03:00"}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update dueDate at '{}' milestone status".format(test_status),
            }
        ],
    }


def test_patch_milestone(app, centralized_milestone):
    """
    milestone owner can patch it
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    request_data = {
        "description": "What?",
        "dueDate": "2001-10-30T11:15:26.641038+03:00",
        "status": Milestone.STATUS_MET,
    }
    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": request_data},
    )
    assert response.status_code == 200

    result_plan = app.app.registry.mongodb.plans.get(plan["id"])
    result = result_plan.get("milestones")[0]

    # fields that haven"t been changed
    assert result["id"] == milestone["id"]
    assert result["author"] == milestone["author"]
    assert result["owner"] == milestone["owner"]
    assert result["owner_token"] == milestone_token
    assert result_plan["dateModified"] == result["dateModified"]

    # changed
    assert result["dueDate"] == request_data["dueDate"]
    assert result["status"] == request_data["status"]
    assert result["description"] == request_data["description"]
    assert result["dateModified"] > milestone["dateModified"]
    assert result["dateModified"] == result["dateMet"] == response.json["data"]["dateMet"]


@pytest.mark.parametrize("test_status", [Milestone.STATUS_NOT_MET, Milestone.STATUS_INVALID])
def test_fail_patch_description(app, centralized_milestone, test_status):
    """
    milestone owner can't patch description if status not in (scheduled, met)
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    # set milestone status
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["milestones"][0]["status"] = test_status
    app.app.registry.mongodb.plans.save(plan_source)

    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": {"description": "Hello"}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update description at '{}' milestone status".format(test_status),
            }
        ],
    }


@pytest.mark.parametrize("test_status", [Milestone.STATUS_MET, Milestone.STATUS_SCHEDULED])
def test_success_patch_description(app, centralized_milestone, test_status):
    """
    milestone owner can patch description if status in (scheduled, met)
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    # set milestone status
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["milestones"][0]["status"] = test_status
    app.app.registry.mongodb.plans.save(plan_source)

    new_description = "Changes are coming"
    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": {"description": new_description}},
        status=200,
    )
    assert response.json["data"]["description"] == new_description


@pytest.mark.parametrize("test_status", [Milestone.STATUS_MET, Milestone.STATUS_NOT_MET])
def test_success_patch_milestone_status(app, centralized_milestone, test_status):
    """
    milestone owner can set its status to met or notMet
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": {"status": test_status}},
    )
    assert response.status_code == 200
    result_plan = app.app.registry.mongodb.plans.get(plan["id"])
    result = result_plan.get("milestones")[0]

    assert result_plan["dateModified"] == result["dateModified"]
    assert result["status"] == test_status
    assert result["dateModified"] > milestone["dateModified"]
    if test_status == Milestone.STATUS_MET:
        assert result["dateModified"] == result["dateMet"]
    else:
        assert "dateMet" not in result


def test_fail_patch_milestone_status(app, centralized_milestone):
    """
    milestone owner can't invalidate it
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    response = app.patch_json(
        "/plans/{}/milestones/{}?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": {"status": Milestone.STATUS_INVALID}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [
            {
                "description": "Can't update milestone status from 'scheduled' to 'invalid'",
                "location": "body",
                "name": "data",
            }
        ],
    }


def test_forbidden_update_milestone_documents(app, centralized_milestone):
    """
    Plan owner or just broker can't manage milestone documents
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    response = app.post_json(
        "/plans/{}/milestones/{}/documents?acc_token={}".format(plan["id"], milestone["id"], plan_token),
        {"data": {}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [{"description": "Forbidden", "location": "url", "name": "permission"}],
    }

    # put
    document = milestone["documents"][0]
    response = app.put_json(
        "/plans/{}/milestones/{}/documents/{}?acc_token={}".format(
            plan["id"], milestone["id"], document["id"], plan_token
        ),
        {"data": {}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [{"description": "Forbidden", "location": "url", "name": "permission"}],
    }

    # patch
    response = app.patch_json(
        "/plans/{}/milestones/{}/documents/{}?acc_token={}".format(
            plan["id"], milestone["id"], document["id"], plan_token
        ),
        {"data": {}},
        status=403,
    )
    assert response.json == {
        "status": "error",
        "errors": [{"description": "Forbidden", "location": "url", "name": "permission"}],
    }


def test_update_milestone_documents(app, centralized_milestone):
    """
    as a milestone owner I can manage it's documents
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    milestone, milestone_token = milestone_data["data"], milestone_data["token"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))
    plan_date_modified = plan["dateModified"]
    milestone_date_modified = milestone["dateModified"]

    request_data = {
        "title": "sign.p7s",
        "url": generate_docservice_url(app),
        "hash": "md5:" + "0" * 32,
        "format": "application/pk7s",
    }
    response = app.post_json(
        "/plans/{}/milestones/{}/documents?acc_token={}".format(plan["id"], milestone["id"], milestone_token),
        {"data": request_data},
    )
    assert response.status_code == 201

    result_plan = app.app.registry.mongodb.plans.get(plan["id"])
    result_milestone = result_plan.get("milestones")[0]
    assert len(result_milestone["documents"]) == 2
    new_doc = result_milestone["documents"][1]
    assert new_doc["title"] == request_data["title"]
    assert new_doc["hash"] == request_data["hash"]
    assert new_doc["format"] == request_data["format"]
    assert result_plan["dateModified"] > plan_date_modified
    plan_date_modified = result_plan["dateModified"]
    assert result_plan["milestones"][0]["dateModified"] > milestone_date_modified
    milestone_date_modified = result_plan["milestones"][0]["dateModified"]

    # put
    request_data = {
        "title": "sign.p7s",
        "url": generate_docservice_url(app),
        "hash": "md5:" + "0" * 32,
        "format": "application/signature",
    }
    response = app.put_json(
        "/plans/{}/milestones/{}/documents/{}?acc_token={}".format(
            plan["id"], milestone["id"], new_doc["id"], milestone_token
        ),
        {"data": request_data},
    )
    assert response.json["data"]["format"] == "application/pk7s"

    request_data = {
        "title": "sign.p7s",
        "url": generate_docservice_url(app),
        "hash": "md5:" + "0" * 32,
        "format": "application/pk7s",
    }
    response = app.put_json(
        "/plans/{}/milestones/{}/documents/{}?acc_token={}".format(
            plan["id"], milestone["id"], new_doc["id"], milestone_token
        ),
        {"data": request_data},
    )
    assert response.status_code == 200

    result_plan = app.app.registry.mongodb.plans.get(plan["id"])
    result_milestone = result_plan.get("milestones")[0]
    assert len(result_milestone["documents"]) == 4
    old_doc = new_doc
    new_doc = result_milestone["documents"][-1]
    assert new_doc["id"] == old_doc["id"]
    assert new_doc["title"] == request_data["title"]
    assert new_doc["hash"] == request_data["hash"]
    assert new_doc["format"] == request_data["format"]
    assert result_plan["dateModified"] > plan_date_modified
    plan_date_modified = result_plan["dateModified"]
    assert result_plan["milestones"][0]["dateModified"] > milestone_date_modified
    milestone_date_modified = result_plan["milestones"][0]["dateModified"]

    # patch
    request_data = {
        "title": "sign-3.p7s",
        "format": "ms/sms",
        "documentOf": "my ma",
        "documentType": "notice",
        "language": "en",
    }
    response = app.patch_json(
        "/plans/{}/milestones/{}/documents/{}?acc_token={}".format(
            plan["id"], milestone["id"], new_doc["id"], milestone_token
        ),
        {"data": request_data},
    )
    assert response.status_code == 200

    result_plan = app.app.registry.mongodb.plans.get(plan["id"])
    result_milestone = result_plan.get("milestones")[0]
    assert len(result_milestone["documents"]) == 4
    patched_doc = result_milestone["documents"][-1]
    assert patched_doc["id"] == new_doc["id"]
    assert patched_doc["hash"] == new_doc["hash"]
    assert patched_doc["url"].split("Signature")[0] == new_doc["url"].split("Signature")[0]
    assert patched_doc["format"] == request_data["format"]
    assert patched_doc["title"] == request_data["title"]
    assert patched_doc["documentOf"] == request_data["documentOf"]
    assert patched_doc["documentType"] == request_data["documentType"]
    assert patched_doc["language"] == request_data["language"]
    assert result_plan["dateModified"] > plan_date_modified
    assert result_plan["milestones"][0]["dateModified"] > milestone_date_modified


@pytest.mark.parametrize(
    "test_statuses",
    [
        (Milestone.STATUS_SCHEDULED, Milestone.STATUS_INVALID),
        (Milestone.STATUS_MET, Milestone.STATUS_INVALID),
        (Milestone.STATUS_NOT_MET, Milestone.STATUS_NOT_MET),
        (Milestone.STATUS_INVALID, Milestone.STATUS_INVALID),
    ],
)
def test_success_patch_plan_procuring_entity_in_time(app, centralized_milestone, test_statuses):
    """
    As plan owner I can change procuringEntity,
    so milestone status becomes "invalid" if it was "scheduled" or "met"
    but "notMet" status should not be changed
    """
    test_status, expected_status = test_statuses
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    # set milestone status
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["milestones"][0]["status"] = test_status
    app.app.registry.mongodb.plans.save(plan_source)

    new_procuring_entity = {
        "id": uuid4().hex,
        "identifier": {"scheme": "UA-EDR", "id": "222222", "legalName": "ЦЗО 2"},
        "name": "ЦЗО 2",
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "kind": "general",
    }
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], plan_token), {"data": {"procuringEntity": new_procuring_entity}}
    )
    assert response.status_code == 200
    assert response.json["data"]["procuringEntity"] == new_procuring_entity
    assert response.json["data"]["milestones"][0]["status"] == expected_status
    assert response.json["data"]["dateModified"] > plan["dateModified"]
    if expected_status == Milestone.STATUS_INVALID and test_status != Milestone.STATUS_INVALID:
        assert response.json["data"]["milestones"][0]["dateModified"] == response.json["data"]["dateModified"]


def test_success_patch_plan_without_invalidating_milestone(app, centralized_milestone):
    """
    As plan owner I can change the plan,
    and milestone should remain "scheduled"
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))
    assert milestone_data["data"]["status"] == "scheduled"

    items = deepcopy(plan["items"])
    items[0]["description"] = "smt"

    response = app.patch_json("/plans/{}?acc_token={}".format(plan["id"], plan_token), {"data": {"items": items}})
    assert response.status_code == 200
    assert response.json["data"]["items"][0]["description"] == "smt"
    assert response.json["data"]["milestones"][0]["status"] == "scheduled"


def test_fail_patch_plan_procuring_entity_not_in_time(app, centralized_milestone):
    """
    As plan owner I can't change procuringEntity later that 2 working days before plan.tender.tenderPeriod.startDate
    if there're milestones in scheduled or met
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    # set plan.tender.tenderPeriod.startDate
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["tender"]["tenderPeriod"]["startDate"] = get_now().isoformat()
    app.app.registry.mongodb.plans.save(plan_source)

    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], plan_token),
        {
            "data": {
                "procuringEntity": {
                    "identifier": {"scheme": "UA-EDR", "id": "222222", "legalName": "ЦЗО 2"},
                    "name": "ЦЗО 2",
                    "address": {
                        "countryName": "Україна",
                        "postalCode": "01220",
                        "region": "м. Київ",
                        "locality": "м. Київ",
                        "streetAddress": "вул. Банкова, 11, корпус 1",
                    },
                    "kind": "general",
                }
            }
        },
        status=403,
    )
    assert response.json == {
        'status': 'error',
        'errors': [
            {
                'description': "Can't update procuringEntity later than 2 business days before tenderPeriod.StartDate",
                'location': 'body',
                'name': 'data',
            }
        ],
    }


@pytest.mark.parametrize("test_status", [Milestone.STATUS_NOT_MET, Milestone.STATUS_INVALID])
def test_success_patch_plan_procuring_entity_not_in_time(app, centralized_milestone, test_status):
    """
    As plan owner I can change procuringEntity later that 2 working days before plan.tender.tenderPeriod.startDate
    if there're no approval milestones in scheduled or met
    """
    milestone_data, plan_data = centralized_milestone["milestone"], centralized_milestone["plan"]
    plan, plan_token = plan_data["data"], plan_data["token"]
    app.authorization = ("Basic", ("broker", "broker"))

    # set plan.tender.tenderPeriod.startDate and milestone status
    plan_source = app.app.registry.mongodb.plans.get(plan["id"])
    plan_source["tender"]["tenderPeriod"]["startDate"] = get_now().isoformat()
    plan_source["milestones"][0]["status"] = test_status
    app.app.registry.mongodb.plans.save(plan_source)

    request_entity = {
        "id": uuid4().hex,
        "identifier": {"scheme": "UA-EDR", "id": "222222", "legalName": "ЦЗО 2"},
        "name": "ЦЗО 2",
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "kind": "general",
    }
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], plan_token),
        {"data": {"procuringEntity": request_entity}},
        status=200,
    )
    assert response.json["data"]["procuringEntity"] == request_entity
