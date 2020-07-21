# -*- coding: utf-8 -*-
from openprocurement.planning.api.tests.base import app, singleton_app, plan, test_plan_data
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
    test_tender_negotiation_quick_data as negotiation_quick_tender_data,
)
from openprocurement.tender.openeu.tests.base import test_tender_data as openeu_tender_data
from openprocurement.tender.openua.tests.base import test_tender_data as openua_tender_data
from openprocurement.tender.openuadefense.tests.base import test_tender_data as defense_tender_data
from openprocurement.tender.cfaselectionua.tests.tender import tender_data as cfa_selection_tender_data
from openprocurement.tender.pricequotation.tests.data import test_tender_data as pricequotation_tender_data
from copy import deepcopy
import pytest


def test_get_plan_tenders_405(app, plan):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.get("/plans/{}/tenders".format(plan["data"]["id"]), status=405)
    assert response.json == {
        u"status": u"error",
        u"errors": [{u"description": u"Method not allowed", u"location": u"request", u"name": u"method"}],
    }


def test_plan_tenders_403(app, plan):
    app.authorization = None
    app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": {}}, status=403)


def test_plan_tenders_404(app):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans/{}/tenders".format("a" * 32), {"data": {}}, status=404)
    assert response.status == "404 Not Found"
    assert response.content_type == "application/json"
    assert response.json == {
        u"status": u"error",
        u"errors": [{u"description": u"Not Found", u"location": u"url", u"name": u"plan_id"}],
    }


def test_plan_tenders_422(app, plan):
    app.authorization = ("Basic", ("broker", "broker"))
    app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": {}}, status=422)


test_below_tender_data = deepcopy(below_tender_data)
test_below_tender_data["procuringEntity"]["identifier"] = test_plan_data["procuringEntity"]["identifier"]
test_below_tender_data["items"] = test_below_tender_data["items"][:1]
test_below_tender_data["items"][0]["classification"] = test_plan_data["items"][0]["classification"]


def test_fail_identifier_id_validation(app):
    app.authorization = ("Basic", ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["procuringEntity"]["identifier"]["id"] = "911"
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    response = app.post_json(
        "/plans/{}/tenders?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {"data": test_below_tender_data},
        status=422,
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procuringEntity"
    plan_identifier = plan["data"]["procuringEntity"]["identifier"]
    tender_identifier = test_below_tender_data["procuringEntity"]["identifier"]
    assert errors[0]["description"] == "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
        plan_identifier["scheme"], plan_identifier["id"], tender_identifier["scheme"], tender_identifier["id"]
    )


def test_fail_identifier_scheme_validation(app):
    app.authorization = ("Basic", ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["procuringEntity"]["identifier"]["scheme"] = "AE-DCCI"
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    response = app.post_json(
        "/plans/{}/tenders?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {"data": test_below_tender_data},
        status=422,
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procuringEntity"
    plan_identifier = plan["data"]["procuringEntity"]["identifier"]
    tender_identifier = test_below_tender_data["procuringEntity"]["identifier"]
    assert errors[0]["description"] == "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
        plan_identifier["scheme"], plan_identifier["id"], tender_identifier["scheme"], tender_identifier["id"]
    )


def test_fail_procurement_method_type_validation(app):
    app.authorization = ("Basic", ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["tender"]["procurementMethodType"] = "aboveThresholdUA"
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    response = app.post_json(
        "/plans/{}/tenders".format(plan["data"]["id"]), {"data": test_below_tender_data}, status=422
    )
    errors = response.json["errors"]
    assert len(errors) == 1
    assert errors[0]["name"] == "procurementMethodType"
    assert errors[0]["description"] == "procurementMethodType doesn't match: aboveThresholdUA != belowThreshold"


def test_procurement_method_type_cpb(app):
    app.authorization = ("Basic", ("broker", "broker"))

    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["tender"]["procurementMethod"] = ""
    request_plan_data["tender"]["procurementMethodType"] = "centralizedProcurement"

    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": test_below_tender_data})
    assert response.status == "201 Created"


def test_success_classification_id(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {"scheme": u"ДК021", "description": "Antiperspirants", "id": "33711120-4"}
    del request_plan_data["items"]

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Make-up preparations",
        "id": "33711200-9",
    }
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data})
    assert response.status == "201 Created"


def test_fail_classification_id(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {
        "scheme": u"ДК021",
        "description": "Personal care products",
        "id": "33700000-7",
    }
    del request_plan_data["items"]

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Antiperspirants",
        "id": "33711120-4",
    }
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data}, status=422)
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error["name"] == "items[0].classification.id"
    assert (
        error["description"] == "Plan classification.id 33700000-7 and item's 33711120-4 "
        "should be of the same group 3370"
    )


def test_success_classification_id_336(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {"scheme": u"ДК021", "description": "Insulin", "id": "33615100-5"}
    del request_plan_data["items"]

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"] = request_tender_data["items"][:1]
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Medicinal products for dermatology",
        "id": "33631000-2",
    }
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data})
    assert response.status == "201 Created"


def test_fail_classification_id_336(app):
    request_plan_data = deepcopy(test_plan_data)
    request_plan_data["classification"] = {
        "scheme": u"ДК021",
        "description": "Pharmaceutical products",
        "id": "33600000-6",
    }
    del request_plan_data["items"]

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": request_plan_data})
    plan = response.json

    request_tender_data = deepcopy(test_below_tender_data)
    request_tender_data["items"] = request_tender_data["items"][:1]
    request_tender_data["items"][0]["classification"] = {
        "scheme": u"ДК021",
        "description": "Makeup kits",
        "id": "33711420-7",
    }
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data}, status=422)
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error["name"] == "items[0].classification.id"
    assert (
        error["description"] == "Plan classification.id 33600000-6 and item's 33711420-7 "
        "should be of the same group 336"
    )


def create_plan_for_tender(app, tender_data, plan_data):
    plan_data["tender"]["procurementMethodType"] = tender_data["procurementMethodType"]
    procedure_values = {procedure: k for k, v in PROCEDURES.items() for procedure in v}
    plan_data["tender"]["procurementMethod"] = procedure_values[tender_data["procurementMethodType"]]

    plan_data["procuringEntity"]["identifier"]["id"] = tender_data["procuringEntity"]["identifier"]["id"]
    plan_data["procuringEntity"]["identifier"]["scheme"] = tender_data["procuringEntity"]["identifier"]["scheme"]

    plan_data["classification"] = tender_data["items"][0]["classification"]
    plan_data["items"][0]["classification"] = plan_data["classification"]
    plan_data["items"][1]["classification"] = plan_data["classification"]
    plan_data["items"][2]["classification"] = plan_data["classification"]

    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans", {"data": plan_data})
    return response.json


def test_fail_tender_creation(app):
    app.authorization = ("Basic", ("broker", "broker"))
    request_tender_data = deepcopy(test_below_tender_data)
    request_plan_data = deepcopy(test_plan_data)
    plan = create_plan_for_tender(app, request_tender_data, request_plan_data)

    # rm milestones that causes data error
    request_tender_data["enquiryPeriod"]["endDate"] = "2019-01-02T00:00:00+02:00"

    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data}, status=422)
    assert response.json == {
        u"status": u"error",
        u"errors": [
            {
                u"description": {u"startDate": [u"period should begin before its end"]},
                u"location": u"body",
                u"name": u"enquiryPeriod",
            }
        ],
    }

    # get plan form db
    plan_from_db = app.app.registry.db.get(plan["data"]["id"])
    assert plan_from_db.get("tender_id") is None


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
    pricequotation_tender_data
]


@pytest.mark.parametrize("request_tender_data", test_tenders)
def test_success_plan_tenders_creation(app, request_tender_data):
    app.authorization = ("Basic", ("broker", "broker"))
    request_plan_data = deepcopy(test_plan_data)

    if request_tender_data["procurementMethodType"] == "aboveThresholdUA.defense":
        request_plan_data['procuringEntity']['kind'] = 'defense'
    plan = create_plan_for_tender(app, request_tender_data, request_plan_data)

    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data})
    assert response.status == "201 Created"

    tender_data = response.json["data"]
    assert tender_data["plans"] == [{"id": plan["data"]["id"]}]
    assert tender_data["title"] == request_tender_data["title"]
    assert response.headers["Location"] == "http://localhost/api/2.5/tenders/{}".format(tender_data["id"])

    # get plan
    response = app.get("/plans/{}".format(plan["data"]["id"]))
    assert response.json["data"]["tender_id"] == tender_data["id"]

    # removing status (if the tender was created before the plan statuses release)
    plan_from_db = app.app.registry.db.get(plan["data"]["id"])
    del plan_from_db["status"]
    app.app.registry.db.save(plan_from_db)

    # add another tender
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data}, status=422)
    error_data = response.json["errors"]
    assert len(error_data) == 1
    error = error_data[0]
    assert error["location"] == "data"
    assert error["name"] == "tender_id"
    assert error["description"] == "This plan has already got a tender"

    # check plan status
    get_response = app.get("/plans/{}".format(plan["data"]["id"]))
    assert get_response.json["data"]["status"] == "complete"


def test_validations_before_and_after_tender(app):
    app.authorization = ("Basic", ("broker", "broker"))
    request_tender_data = deepcopy(below_tender_data)
    request_plan_data = deepcopy(test_plan_data)
    plan = create_plan_for_tender(app, request_tender_data, request_plan_data)

    # changing procuringEntity
    pe_change = {
        "identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
        "name": u"ДУС",
    }
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {"data": {"procuringEntity": pe_change}},
    )
    assert response.status == "200 OK"

    # adding tender
    request_tender_data["procuringEntity"]["identifier"]["id"] = pe_change["identifier"]["id"]
    request_tender_data["procuringEntity"]["identifier"]["scheme"] = pe_change["identifier"]["scheme"]
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data})
    assert response.status == "201 Created"

    # removing status (if the tender was created before the plan statuses release)
    plan_from_db = app.app.registry.db.get(plan["data"]["id"])
    del plan_from_db["status"]
    app.app.registry.db.save(plan_from_db)

    response = app.get("/plans/{}".format(plan["data"]["id"]))
    assert response.json["data"]["status"] == "complete"

    # try to change procuringEntity
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {
            "data": {
                "procuringEntity": {
                    "identifier": {
                        "scheme": u"UA-EDR",
                        "id": u"111983",
                        "legalName": u"ДП Державне Управління Справами",
                    },
                    "name": u"ДУС",
                }
            }
        },
        status=422,
    )
    assert response.json == {
        u"status": u"error",
        u"errors": [
            {
                u"description": u"Changing this field is not allowed after tender creation",
                u"location": u"data",
                u"name": u"procuringEntity",
            }
        ],
    }

    # try to change budgetBreakdown
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {"data": {"budget": {"breakdown": [{"description": "Changed description"}]}}},
        status=422,
    )
    assert response.json == {
        u"status": u"error",
        u"errors": [
            {
                u"description": u"Changing this field is not allowed after tender creation",
                u"location": u"data",
                u"name": u"budget.breakdown",
            }
        ],
    }

    # try to change anything except procuringEntity and budgetBreakdown
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {
            "data": {
                "procurementMethodType": "whatever",
                "items": [
                    {"classification": {"scheme": u"ДК021", "description": "Antiperspirants", "id": "33711120-4"}}
                ],
                "classification": {"scheme": u"ДК021", "description": "Antiperspirants", "id": "33711120-4"},
            }
        },
    )
    assert response.status == "200 OK"

    # try again
    response = app.patch_json(
        "/plans/{}?acc_token={}".format(plan["data"]["id"], plan["access"]["token"]),
        {"data": {"procurementMethodType": "another"}},
        status=422,
    )
    assert response.json == {
        "status": "error",
        "errors": [{"location": "data", "name": "status", "description": "Can't update plan in 'complete' status"}],
    }


def test_tender_creation_modified_date(app):
    app.authorization = ("Basic", ("broker", "broker"))
    request_plan_data = deepcopy(test_plan_data)
    plan = create_plan_for_tender(app, below_tender_data, request_plan_data)

    # get feed last links
    response = app.get("/plans")
    date_feed = response.json
    assert len(date_feed["data"]) == 1
    assert date_feed["data"][0]["id"] == plan["data"]["id"]
    assert date_feed["data"][0]["dateModified"] == plan["data"]["dateModified"]

    response = app.get("/plans?feed=changes")
    change_feed = response.json
    assert len(change_feed["data"]) == 1
    assert change_feed["data"][0]["id"] == plan["data"]["id"]
    assert change_feed["data"][0]["dateModified"] == plan["data"]["dateModified"]

    # post tender
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": below_tender_data})
    assert response.status == "201 Created"

    # get updated plan
    response = app.get("/plans/{}".format(plan["data"]["id"]))
    updated_plan = response.json
    assert updated_plan["data"]["dateModified"] > plan["data"]["dateModified"]
    assert updated_plan["data"]["status"] == "complete"

    # check feeds are not empty
    response = app.get("/" + date_feed["next_page"]["path"].split("/")[-1])
    new_date_feed = response.json
    assert len(new_date_feed["data"]) == 1
    assert new_date_feed["data"][0]["id"] == plan["data"]["id"]

    response = app.get("/plans?feed=changes&offset={}".format(change_feed["next_page"]["offset"]))
    new_change_feed = response.json
    assert len(new_change_feed["data"]) == 1
    assert new_change_feed["data"][0]["id"] == plan["data"]["id"]


@pytest.mark.parametrize("request_tender_data", test_tenders)
def test_fail_pass_plans(app, plan, request_tender_data):
    """
    "plans" field cannot be set via 'data'
    """
    app.authorization = ("Basic", ("broker", "broker"))
    tender_data = dict(**request_tender_data)
    tender_data["plans"] = [{"id": plan["data"]["id"]}]
    response = app.post_json("/tenders", {"data": request_tender_data})
    assert response.status == "201 Created"
    tender_data = response.json["data"]

    assert "plans" not in tender_data  # NOT in
    assert tender_data["title"] == request_tender_data["title"]


def test_fail_cfa_second_stage_creation(app, plan):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json(
        "/plans/{}/tenders".format(plan["data"]["id"]), {"data": cfa_selection_tender_data}, status=422
    )
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error["name"] == "procurementMethodType"
    assert error["description"].startswith(u"Should be one of the first stage values:")


@pytest.mark.parametrize("request_tender_data", [cd_stage2_data_ua, cd_stage2_data_eu])
def test_fail_cd_second_stage_creation(app, plan, request_tender_data):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data}, status=403)
    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error["name"] == "accreditation"
    assert u"Broker Accreditation level does not permit tender creation" == error["description"]


def test_fail_tender_creation_without_budget_breakdown(app):
    app.authorization = ("Basic", ("broker", "broker"))
    request_plan_data = deepcopy(test_plan_data)
    request_tender_data = deepcopy(test_below_tender_data)
    del request_plan_data["budget"]["breakdown"]
    plan = create_plan_for_tender(app, request_tender_data, request_plan_data)

    assert "breakdown" not in plan["data"]["budget"]

    response = app.post_json("/plans/{}/tenders".format(plan["data"]["id"]), {"data": request_tender_data}, status=422)

    error_data = response.json["errors"]
    assert len(error_data) > 0
    error = error_data[0]
    assert error["location"] == "data"
    assert error["name"] == "budget.breakdown"
    assert error["description"] == "Plan should contain budget breakdown"

    # get plan form db
    plan_from_db = app.app.registry.db.get(plan["data"]["id"])
    assert plan_from_db.get("tender_id") is None
