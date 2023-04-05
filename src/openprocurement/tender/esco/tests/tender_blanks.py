# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import CPV_ITEMS_CLASS_FROM, NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM
from openprocurement.api.utils import get_now, parse_date
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.tests.criteria_utils import add_criteria, generate_responses


# TenderESCOTest

def tender_value(self):
    invalid_data = deepcopy(self.initial_data)
    value = {"value": {"amount": 100}}
    invalid_data["value"] = value
    response = self.app.post_json("/tenders", {"data": invalid_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "value"}]
    )

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"value": {"amount": 100}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "value"}]
    )


def tender_min_value(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertIn("minValue", response.json["data"])
    self.assertEqual(response.json["data"]["minValue"]["amount"], 0)
    self.assertEqual(response.json["data"]["minValue"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"minValue": {"amount": 1500}}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "minValue",
            "description": "Rogue field"
        }]
    )


def tender_minimal_step_invalid(self):
    data = deepcopy(self.initial_data)
    data["minimalStep"] = {"amount": 100}
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "minimalStep",
            "description": "Rogue field"
        }]
    )


def tender_yearlyPaymentsPercentageRange_invalid(self):
    data = deepcopy(self.initial_data)
    data["yearlyPaymentsPercentageRange"] = 0.6
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"],
                "location": "body",
                "name": "yearlyPaymentsPercentageRange",
            }
        ],
    )

    data["fundingKind"] = "budget"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["fundingKind"], "budget")
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_token),
        {"data": {"yearlyPaymentsPercentageRange": 1}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
                ],
                "location": "body",
                "name": "yearlyPaymentsPercentageRange",
            }
        ],
    )


def tender_yearlyPaymentsPercentageRange(self):
    data = deepcopy(self.initial_data)
    del data["yearlyPaymentsPercentageRange"]

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.8)
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_token),
        {"data": {"fundingKind": "budget", "yearlyPaymentsPercentageRange": 0.31456}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["fundingKind"], "budget")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.31456)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_token), {"data": {"fundingKind": "other"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"],
                "location": "body",
                "name": "yearlyPaymentsPercentageRange",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_token),
        {"data": {"fundingKind": "other", "yearlyPaymentsPercentageRange": 0.8}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["fundingKind"], "other")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.8)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_token),
        {"data": {"yearlyPaymentsPercentageRange": 1}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"],
                "location": "body",
                "name": "yearlyPaymentsPercentageRange",
            }
        ],
    )

    data["fundingKind"] = "budget"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.8)


def tender_fundingKind_default(self):
    data = deepcopy(self.initial_data)
    del data["fundingKind"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    # when no fundingKind field in initial data, default value should be set
    self.assertEqual(response.json["data"]["fundingKind"], "other")


def items_without_deliveryDate_quantity(self):
    self.assertEqual(len(self.initial_data["items"]), 1)
    for item in self.initial_data["items"]:
        self.assertIn("deliveryDate", item)
        self.assertIn("quantity", item)

    # create role
    tender_data = deepcopy(self.initial_data)
    tender_data["status"] = "draft"

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "draft")
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    for item in response.json["data"]["items"]:
        self.assertNotIn("deliveryDate", item)
        self.assertNotIn("quantity", item)

    # edit_draft role
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": [{"quantity": 5}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    for item in response.json["data"]["items"]:
        self.assertNotIn("deliveryDate", item)
        self.assertNotIn("quantity", item)

    add_criteria(self)
    # edit_active.tendering role
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": [{"quantity": 5}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    for item in response.json["data"]["items"]:
        self.assertNotIn("deliveryDate", item)
        self.assertNotIn("quantity", item)

    # award preparation

    # post bids
    for bid_data in self.test_bids_data:
        bid, bid_token = self.create_bid(self.tender_id, bid_data)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id),
                                  {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.award_id = response.json["data"][0]["id"]
    self.app.authorization = ("Basic", ("broker", ""))

    # qualify award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {
            "data": {
                "status": "active",
                "qualified": True,
                "eligible": True,
                "items": [
                    {
                        "description": "футляри до державних нагород",
                        "description_en": "Cases for state awards",
                        "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
                        "additionalClassifications": [
                            {
                                "scheme": "ДКПП",
                                "id": "17.21.1",
                                "description": "папір і картон гофровані, паперова й картонна тара",
                            }
                        ],
                        "unit": {"name": "item", "code": "KGM"},
                        "quantity": 5,
                        "deliveryDate": {
                            "startDate": (get_now() + timedelta(days=2)).isoformat(),
                            "endDate": (get_now() + timedelta(days=5)).isoformat(),
                        },
                        "deliveryAddress": {
                            "countryName": "Україна",
                            "postalCode": "79000",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "streetAddress": "вул. Банкова 1",
                        },
                    }
                ],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]["contracts"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amountNet": contract["value"]["amount"] - 1}}},
    )

    contract["items"][0]["quantity"] = 10
    contract["items"][0]["deliveryDate"] = {
        "startDate": (get_now() + timedelta(days=12)).isoformat(),
        "endDate": (get_now() + timedelta(days=15)).isoformat(),
    }
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "status": "pending",
                "items": contract["items"],
            }
        },
        status=403
    )
    self.assertEqual(
        response.json["errors"][0]["description"], "Updated could be only unit.value.amount in item"
    )


def tender_noticePublicationDate(self):
    # create in draft
    tender_data = deepcopy(self.initial_data)
    tender_data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("noticePublicationDate", response.json["data"])
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    add_criteria(self)
    # set active.tendering status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("noticePublicationDate", response.json["data"])
    publication_date = response.json["data"]["noticePublicationDate"]

    # try to patch noticePublicationDate in tendering
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"noticePublicationDate": (get_now() + timedelta(minutes=30)).isoformat()}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "noticePublicationDate",
            "description": "Rogue field"
        }]
    )


# TestTenderEU


def create_tender_invalid(self):
    request_path = "/tenders"

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "esco", "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "esco", "minValue": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Please use a mapping for this field or Value instance instead of str."],
                "location": "body",
                "name": "minValue",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "esco", "procurementMethod": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": ["Value must be one of ['open']."],
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "tenderPeriod"},
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "esco", "enquiryPeriod": {"endDate": "invalid_value"}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"endDate": ["Could not parse invalid_value. Should be ISO8601."]},
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "esco", "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"endDate": ["date value out of range"]}, "location": "body", "name": "enquiryPeriod"}],
    )

    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2014-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"startDate": ["period should begin before its end"]},
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    self.initial_data["tenderPeriod"]["startDate"] = (get_now() - timedelta(minutes=30)).isoformat()
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    del self.initial_data["tenderPeriod"]["startDate"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["tenderPeriod.startDate should be in greater than current date"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    now = get_now()
    self.initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"],
          "location": "body", "name": "awardPeriod"}],
    )

    self.initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=35)).isoformat(),
        "endDate": (now + timedelta(days=35)).isoformat(),
    }
    self.initial_data["awardPeriod"] = {
        "startDate": (now + timedelta(days=34)).isoformat(),
        "endDate": (now + timedelta(days=34)).isoformat(),
    }
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    del self.initial_data["auctionPeriod"]
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after auctionPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    data = deepcopy(self.initial_data)
    data["minimalStepPercentage"] = 0.001
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value should be greater than 0.005."],
                "location": "body",
                "name": "minimalStepPercentage",
            }
        ],
    )
    data["minimalStepPercentage"] = 0.5
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value should be less than 0.03."],
                "location": "body",
                "name": "minimalStepPercentage",
            }
        ],
    )

    data = self.initial_data["fundingKind"]
    self.initial_data["fundingKind"] = "invalid funding kind"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value must be one of ['budget', 'other']."],
                "location": "body",
                "name": "fundingKind",
            }
        ],
    )
    self.initial_data["fundingKind"] = data

    data = self.initial_data["items"][0].pop("additionalClassifications")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]["classification"]["id"]
        self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    status = 422 if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM else 201
    response = self.app.post_json(request_path, {
        "data": self.initial_data,
        "config": self.initial_config,
    }, status=status)
    self.initial_data["items"][0]["additionalClassifications"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]["classification"]["id"] = cpv_code
    if status == 201:
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
    else:
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": [{"additionalClassifications": ["This field is required."]}],
                    "location": "body",
                    "name": "items",
                }
            ],
        )

    data = self.initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]["classification"]["id"]
        self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": [
                        {
                            "additionalClassifications": [
                                "One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."
                            ]
                        }
                    ],
                    "location": "body",
                    "name": "items",
                }
            ],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": [
                        {
                            "additionalClassifications": [
                                "One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."
                            ]
                        }
                    ],
                    "location": "body",
                    "name": "items",
                }
            ],
        )

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33611000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.assertEqual(response.status, "201 Created")

    data = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    del self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"contactPoint": {"email": ["telephone or email should be present"]}},
                "location": "body",
                "name": "procuringEntity",
            }
        ],
    )
    correct_phone = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = "++223"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = correct_phone
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u'description': {u'contactPoint': {u'telephone': [u'wrong telephone format (could be missed +)']}},
                u'location': u'body',
                u'name': u'procuringEntity'
            }
        ]
    )

    data = self.initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = "19212310-1"
    data["classification"] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
    )

    new_item = deepcopy(self.initial_data["items"][0])
    new_item["classification"]["id"] = "44620000-2"
    self.initial_data["items"].append(new_item)

    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
    )
    self.initial_data["items"].pop()


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn(response.json["data"]["id"], response.headers["Location"])
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    tender_set = set(tender)
    if "procurementMethodDetails" in tender_set:
        tender_set.remove("procurementMethodDetails")
    self.assertEqual(
        tender_set - set(self.initial_data),
        {
            "id",
            "criteria",
            "dateModified",
            "dateCreated",
            "enquiryPeriod",
            "complaintPeriod",
            "tenderID",
            "status",
            "procurementMethod",
            "awardCriteria",
            "submissionMethod",
            "next_check",
            "owner",
            "date",
            "noticePublicationDate",
        },
    )


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": {"endDate": tender["tenderPeriod"]["endDate"]}}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "tenderPeriod",
            "description": {
                "startDate": [
                    "This field is required."
                ]
            }
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": {
            "startDate": tender["enquiryPeriod"]["endDate"],
            "endDate": tender["tenderPeriod"]["endDate"],
        }}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "tenderPeriod",
            "description": ["tenderPeriod must be at least 30 full calendar days long"]
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("invalidationDate", response.json["data"]["enquiryPeriod"])
    new_tender = response.json["data"]
    new_enquiryPeriod = new_tender.pop("enquiryPeriod")
    new_dateModified = new_tender.pop("dateModified")
    tender.pop("enquiryPeriod")
    tender["procurementMethodRationale"] = "Open"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertTrue(
        any(
            [
                i
                for i in revisions[-1]["changes"]
                if i["op"] == "remove" and i["path"] == "/procurementMethodRationale"
            ]
        )
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422
    )

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "procuringEntity",
            "description": "Can't change procuringEntity.kind in a public tender"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0], self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)
    new_dateModified2 = response.json["data"]["dateModified"]

    item = deepcopy(self.initial_data["items"][0])
    item["classification"] = {
        "scheme": "CPV",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [item]
            }
        },
        status=422,
    )

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = [
        tender["items"][0]["additionalClassifications"][0] for i in range(3)
    ]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [item]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = tender["items"][0]["additionalClassifications"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]

    period = {
        "startDate": calculate_tender_business_date(
            parse_date(new_dateModified2), -timedelta(3), None, True
        ).isoformat(),
        "endDate": new_dateModified2
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"enquiryPeriod": period}},
    )
    result = response.json["data"]
    self.assertNotEqual(period["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertNotEqual(period["endDate"], result["enquiryPeriod"]["endDate"])
    self.assertEqual(tender["enquiryPeriod"]["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertEqual(tender["enquiryPeriod"]["endDate"], result["enquiryPeriod"]["endDate"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {"description": {"valueAddedTaxIncluded": "Rogue field"}, "location": "body", "name": "guarantee"},
    )

    guarantee = {"amount": 12, "currency": "UAH"}
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"guarantee": guarantee}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    guarantee["currency"] = "USD"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": guarantee}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"minimalStepPercentage": 0.02516}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["minimalStepPercentage"], 0.02516)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"fundingKind": "budget"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["fundingKind"], "budget")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"fundingKind": "other"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["fundingKind"], "other")

    # response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.auction'}})
    # self.assertEqual(response.status, '200 OK')

    # response = self.app.get('/tenders/{}'.format(tender['id']))
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('auctionUrl', response.json['data'])

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def tender_with_nbu_discount_rate(self):
    data = deepcopy(self.initial_data)
    del data["NBUdiscountRate"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "NBUdiscountRate"}],
    )

    data = deepcopy(self.initial_data)
    del data["milestones"]
    data.update({"id": "hash", "NBUdiscountRate": 0.22986})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["NBUdiscountRate"], 0.22986)
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]

    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    if "noticePublicationDate" in tender:
        tender.pop("noticePublicationDate")
    self.assertEqual(
        set(tender),
        {
            "procurementMethodType",
            "id",
            "criteria",
            "dateModified",
            "dateCreated",
            "tenderID",
            "status",
            "enquiryPeriod",
            "tenderPeriod",
            "complaintPeriod",
            "items",
            "minValue",
            "owner",
            "minimalStepPercentage",
            "procuringEntity",
            "next_check",
            "procurementMethod",
            "awardCriteria",
            "submissionMethod",
            "title",
            "title_en",
            "date",
            "NBUdiscountRate",
            "fundingKind",
            "yearlyPaymentsPercentageRange",
            "mainProcurementCategory",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"NBUdiscountRate": 1.2}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Value should be less than 0.99."], "location": "body", "name": "NBUdiscountRate"}],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"NBUdiscountRate": -2}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Value should be greater than 0."], "location": "body", "name": "NBUdiscountRate"}],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"NBUdiscountRate": 0.39876}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("NBUdiscountRate", response.json["data"])
    self.assertEqual(response.json["data"]["NBUdiscountRate"], 0.39876)


def tender_features_invalid(self):
    data = self.initial_data.copy()
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item, item.copy()]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Item id should be uniq for all items"], "location": "body", "name": "items"}],
    )
    data["items"][0]["id"] = "0"
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "lot",
            "title": "Потужність всмоктування",
            "enum": [{"value": 0.1, "title": "До 1000 Вт"}, {"value": 0.15, "title": "Більше 1000 Вт"}],
        }
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ["This field is required."]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["relatedItem"] = "2"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ["relatedItem should be one of lots"]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["featureOf"] = "item"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ["relatedItem should be one of items"]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["relatedItem"] = "1"
    data["features"][0]["enum"][0]["value"] = 0.5
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": [{"value": ["Float value should be less than 0.25."]}]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.15
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": ["Feature value should be uniq for feature"]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.1
    data["features"].append(data["features"][0].copy())
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Feature code should be uniq for all features"],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][1]["code"] = "OCDS-123454-YEARS"
    data["features"][1]["enum"][0]["value"] = 0.2
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Sum of max value of all features should be less then or equal to 25%"],
                "location": "body",
                "name": "features",
            }
        ],
    )


def tender_features(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = "+0440000000"
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.01, "title": "До 1000 Вт"}, {"value": 0.04, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": "Років на ринку",
            "title_en": "Years trading",
            "description": "Кількість років, які організація учасник працює на ринку",
            "enum": [{"value": 0.03, "title": "До 3 років"}, {"value": 0.07, "title": "Більше 3 років"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.03, "title": "До 90 днів"}, {"value": 0.07, "title": "Більше 90 днів"}],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["features"], data["features"])

    features = deepcopy(data["features"])
    features[0].update({"featureOf": "tenderer", "relatedItem": None})
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"features": features}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("features", response.json["data"])
    self.assertNotIn("relatedItem", response.json["data"]["features"][0])

    pq_entity = deepcopy(data["procuringEntity"])
    pq_entity["contactPoint"]["faxNumber"] = None
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"procuringEntity": pq_entity}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("features", response.json["data"])
    self.assertNotIn("faxNumber", response.json["data"]["procuringEntity"]["contactPoint"])

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"features": []}})
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("features", response.json["data"])


def invalid_bid_tender_features(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    data = deepcopy(self.initial_data)
    data["features"] = [
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        }
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update({"parameters": [{"code": "OCDS-123454-POSTPONEMENT", "value": 0.1}]})
    invalid_bid_data = deepcopy(bid_data)
    invalid_bid_data.update({"value": {"amount": 500}})
    response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": invalid_bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "value",
                "description": {
                    "contractDuration": ["This field is required."],
                    "annualCostsReduction": ["This field is required."],
                    "yearlyPaymentsPercentage": ["This field is required."],
                },
            }
        ],
    )

    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]

    features = deepcopy(data["features"])
    features[0]["code"] = "OCDS-123-POSTPONEMENT"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"features": features}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["features"][0]["code"])

    parameters = deepcopy(bid["parameters"])
    parameters[0]["code"] = "OCDS-123-POSTPONEMENT"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"parameters": parameters, "status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["parameters"][0]["code"])

    features[0]["enum"][0]["value"] = 0.2
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"features": features}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(0.2, response.json["data"]["features"][0]["enum"][0]["value"])

    parameters[0]["value"] = 0.2
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"parameters": parameters, "status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["parameters"][0]["code"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"features": []}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("features", response.json["data"])

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def create_tender_generated(self):
    data = self.initial_data.copy()
    del data["milestones"]
    # del data['awardPeriod']
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    if "noticePublicationDate" in tender:
        tender.pop("noticePublicationDate")
    self.assertEqual(
        set(tender),
        {
            "procurementMethodType",
            "id",
            "criteria",
            "dateModified",
            "dateCreated",
            "tenderID",
            "status",
            "enquiryPeriod",
            "tenderPeriod",
            "complaintPeriod",
            "items",
            "minValue",
            "owner",
            "minimalStepPercentage",
            "procuringEntity",
            "next_check",
            "procurementMethod",
            "NBUdiscountRate",
            "awardCriteria",
            "submissionMethod",
            "title",
            "title_en",
            "date",
            "fundingKind",
            "yearlyPaymentsPercentageRange",
            "mainProcurementCategory",
        }
    )
    self.assertNotEqual(data["id"], tender["id"])


def patch_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    tender_period = {
        "startDate": (get_now() + timedelta(days=2)).isoformat(),
        "endDate": (get_now() + timedelta(days=33)).isoformat(),
    }

    item = deepcopy(tender["items"][0])
    item.update(description="test item", id="0" * 32)
    tender_patch_data = {
        "items": [item],
        "features": [
            {
                "title": "test feature",
                "relatedItem": "0" * 32,
                "enum": [{"value": 0.1, "title": "test feature value"}],
            }
        ],
        "tenderPeriod": tender_period,
    }

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": tender_patch_data
        }
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("items", tender)
    self.assertEqual(len(tender["items"]), 1)
    self.assertEqual(tender["items"][0]["description"], "test item")
    self.assertEqual(tender["tenderPeriod"], tender_period)
    self.assertEqual(len(tender["features"]), 1)
    self.assertEqual(tender["features"][0]["title"], "test feature")
    self.assertEqual(tender["features"][0]["enum"][0]["value"], 0.1)
