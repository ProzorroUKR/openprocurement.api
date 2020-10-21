# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from iso8601 import parse_date

from openprocurement.api.constants import CPV_ITEMS_CLASS_FROM, NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM
from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.esco.models import TenderESCO
from openprocurement.tender.core.tests.criteria_utils import add_criteria, generate_responses


# TenderESCOTest


def simple_add_tender(self):
    u = TenderESCO(self.initial_data)
    u.tenderID = "UA-X"
    u.noticePublicationDate = get_now().isoformat()

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "esco"
    assert fromdb["procurementMethodType"] == "esco"

    u.delete_instance(self.db)


def tender_value(self):
    invalid_data = deepcopy(self.initial_data)
    value = {"value": {"amount": 100}}
    invalid_data["value"] = value
    response = self.app.post_json("/tenders", {"data": invalid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"value"}]
    )

    response = self.app.post_json("/tenders", {"data": self.initial_data})
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
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"value"}]
    )


def tender_min_value(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertIn("minValue", response.json["data"])
    self.assertEqual(response.json["data"]["minValue"]["amount"], 0)
    self.assertEqual(response.json["data"]["minValue"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"minValue": {"amount": 1500}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("minValue", response.json["data"])
    self.assertEqual(response.json["data"]["minValue"]["amount"], 0)
    self.assertEqual(response.json["data"]["minValue"]["currency"], "UAH")


def tender_minimal_step_invalid(self):
    data = deepcopy(self.initial_data)
    data["minimalStep"] = {"amount": 100}
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertNotIn("minimalStep", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"minimalStep": {"amount": 100}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("minimalStep", response.json["data"])


def tender_yearlyPaymentsPercentageRange_invalid(self):
    data = deepcopy(self.initial_data)
    data["yearlyPaymentsPercentageRange"] = 0.6
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"],
                u"location": u"body",
                u"name": u"yearlyPaymentsPercentageRange",
            }
        ],
    )

    data["fundingKind"] = "budget"
    response = self.app.post_json("/tenders", {"data": data})
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
                u"description": [
                    u"when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
                ],
                u"location": u"body",
                u"name": u"yearlyPaymentsPercentageRange",
            }
        ],
    )


def tender_yearlyPaymentsPercentageRange(self):
    data = deepcopy(self.initial_data)
    del data["yearlyPaymentsPercentageRange"]

    response = self.app.post_json("/tenders", {"data": data})
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
                u"description": [u"when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"],
                u"location": u"body",
                u"name": u"yearlyPaymentsPercentageRange",
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
                u"description": [u"when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"],
                u"location": u"body",
                u"name": u"yearlyPaymentsPercentageRange",
            }
        ],
    )

    data["fundingKind"] = "budget"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["yearlyPaymentsPercentageRange"], 0.8)


def tender_fundingKind_default(self):
    data = deepcopy(self.initial_data)
    del data["fundingKind"]
    response = self.app.post_json("/tenders", {"data": data})
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

    response = self.app.post_json("/tenders", {"data": tender_data})
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
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (draft) status")

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
        bid_data = bid_data.copy()
        rrs = generate_responses(self)
        if rrs:
            bid_data["requirementResponses"] = rrs
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
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
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}})
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
                        "description": u"футляри до державних нагород",
                        "description_en": u"Cases for state awards",
                        "classification": {"scheme": u"ДК021", "id": u"44617100-9", "description": u"Cartons"},
                        "additionalClassifications": [
                            {
                                "scheme": u"ДКПП",
                                "id": u"17.21.1",
                                "description": u"папір і картон гофровані, паперова й картонна тара",
                            }
                        ],
                        "unit": {"name": u"item", "code": u"44617100-9"},
                        "quantity": 5,
                        "deliveryDate": {
                            "startDate": (get_now() + timedelta(days=2)).isoformat(),
                            "endDate": (get_now() + timedelta(days=5)).isoformat(),
                        },
                        "deliveryAddress": {
                            "countryName": u"Україна",
                            "postalCode": "79000",
                            "region": u"м. Київ",
                            "locality": u"м. Київ",
                            "streetAddress": u"вул. Банкова 1",
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

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "status": "pending",
                "items": [
                    {
                        "quantity": 10,
                        "deliveryDate": {
                            "startDate": (get_now() + timedelta(days=12)).isoformat(),
                            "endDate": (get_now() + timedelta(days=15)).isoformat(),
                        },
                    }
                ],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.body, "null")

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertEqual(len(contract["items"]), 1)

    for item in contract["items"]:
        self.assertNotIn("deliveryDate", item)
        self.assertNotIn("quantity", item)


def tender_noticePublicationDate(self):
    # create in active tendering
    tender_data = deepcopy(self.initial_data)
    tender_data["status"] = "active.tendering"
    tender_data["noticePublicationDate"] = (get_now() + timedelta(minutes=30)).isoformat()

    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("noticePublicationDate", response.json["data"])
    self.assertNotEqual(response.json["data"]["noticePublicationDate"], tender_data["noticePublicationDate"])

    # create in draft
    tender_data = deepcopy(self.initial_data)
    tender_data["status"] = "draft"
    tender_data["noticePublicationDate"] = (get_now() + timedelta(minutes=30)).isoformat()

    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("noticePublicationDate", response.json["data"])
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    # try to set noticePublicationDate in draft
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"noticePublicationDate": (get_now() + timedelta(minutes=30)).isoformat()}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (draft) status")

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
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["noticePublicationDate"], publication_date)

    # award preparation

    # post bids
    for bid_data in self.test_bids_data:
        bid_data = bid_data.copy()
        rrs = generate_responses(self)
        if rrs:
            bid_data["requirementResponses"] = rrs
        response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # try to patch noticePublicationDate in pre-qualification
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"noticePublicationDate": (get_now() + timedelta(minutes=30)).isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["noticePublicationDate"], publication_date)

    # qualify bids
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

    # try to patch noticePublicationDate in pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"noticePublicationDate": (get_now() + timedelta(minutes=30)).isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["noticePublicationDate"], publication_date)

    # switch to active.auction
    self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(response.json["data"]["noticePublicationDate"], publication_date)


# TestTenderEU


def create_tender_invalid(self):
    request_path = "/tenders"
    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Content-Type header should be one of ['application/json']",
                u"location": u"header",
                u"name": u"Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"No JSON object could be decoded", u"location": u"body", u"name": u"data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"data": {"procurementMethodType": "invalid_value"}}, status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Not implemented", u"location": u"data", u"name": u"procurementMethodType"}],
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "esco", "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
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
                u"description": [u"Please use a mapping for this field or Value instance instead of unicode."],
                u"location": u"body",
                u"name": u"minValue",
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
            u"description": [u"Value must be one of ['open', 'selective', 'limited']."],
            u"location": u"body",
            u"name": u"procurementMethod",
        },
        response.json["errors"],
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"tenderPeriod"},
        response.json["errors"],
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
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
                u"description": {u"endDate": [u"Could not parse invalid_value. Should be ISO8601."]},
                u"location": u"body",
                u"name": u"enquiryPeriod",
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
        [{u"description": {u"endDate": [u"date value out of range"]}, u"location": u"body", u"name": u"enquiryPeriod"}],
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
                u"description": {u"startDate": [u"period should begin before its end"]},
                u"location": u"body",
                u"name": u"tenderPeriod",
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
                u"description": [u"tenderPeriod.startDate should be in greater than current date"],
                u"location": u"body",
                u"name": u"tenderPeriod",
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
        [{u"description": [u"period should begin after tenderPeriod"], u"location": u"body", u"name": u"awardPeriod"}],
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
        [{u"description": [u"period should begin after auctionPeriod"], u"location": u"body", u"name": u"awardPeriod"}],
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
                u"description": [u"Value should be greater than 0.005."],
                u"location": u"body",
                u"name": u"minimalStepPercentage",
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
                u"description": [u"Value should be less than 0.03."],
                u"location": u"body",
                u"name": u"minimalStepPercentage",
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
                u"description": [u"Value must be one of ['budget', 'other']."],
                u"location": u"body",
                u"name": u"fundingKind",
            }
        ],
    )
    self.initial_data["fundingKind"] = data

    data = self.initial_data["items"][0].pop("additionalClassifications")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]["classification"]["id"]
        self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    status = 422 if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM else 201
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=status)
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
                    u"description": [{u"additionalClassifications": [u"This field is required."]}],
                    u"location": u"body",
                    u"name": u"items",
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
                    u"description": [
                        {
                            u"additionalClassifications": [
                                u"One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."
                            ]
                        }
                    ],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"description": [
                        {
                            u"additionalClassifications": [
                                u"One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."
                            ]
                        }
                    ],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = u"33611000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data})
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
                u"description": {u"contactPoint": {u"email": [u"telephone or email should be present"]}},
                u"location": u"body",
                u"name": u"procuringEntity",
            }
        ],
    )

    data = self.initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = u"19212310-1"
    data["classification"] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"CPV group of items be identical"], u"location": u"body", u"name": u"items"}],
    )

    new_item = deepcopy(self.initial_data["items"][0])
    new_item["classification"]["id"] = u"44620000-2"
    self.initial_data["items"].append(new_item)

    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"CPV class of items should be identical"], u"location": u"body", u"name": u"items"}],
    )
    self.initial_data["items"].pop()


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_set = set(tender)
    if "procurementMethodDetails" in tender_set:
        tender_set.remove("procurementMethodDetails")
    self.assertEqual(
        tender_set - set(self.initial_data),
        set(
            [
                u"id",
                u"dateModified",
                u"enquiryPeriod",
                u"auctionPeriod",
                u"complaintPeriod",
                u"tenderID",
                u"status",
                u"procurementMethod",
                u"awardCriteria",
                u"submissionMethod",
                u"next_check",
                u"owner",
                u"date",
                u"noticePublicationDate",
            ]
        ),
    )
    self.assertIn(tender["id"], response.headers["Location"])


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": {"startDate": tender["enquiryPeriod"]["endDate"]}}},
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

    revisions = self.db.get(tender["id"]).get("revisions")
    self.assertTrue(
        any(
            [
                i
                for i in revisions[-1][u"changes"]
                if i["op"] == u"remove" and i["path"] == u"/procurementMethodRationale"
            ]
        )
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"dateModified": new_dateModified}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender2 = response.json["data"]
    new_enquiryPeriod2 = new_tender2.pop("enquiryPeriod")
    new_dateModified2 = new_tender2.pop("dateModified")
    self.assertEqual(new_tender, new_tender2)
    self.assertNotEqual(new_enquiryPeriod, new_enquiryPeriod2)
    self.assertNotEqual(new_dateModified, new_dateModified2)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procuringEntity": {"kind": "defense"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["procuringEntity"]["kind"], "defense")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [{}, self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [{}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [
                    {
                        "classification": {
                            "scheme": "CPV",
                            "id": "55523100-3",
                            "description": "Послуги з харчування у школах",
                        }
                    }
                ]
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [
                    {
                        "additionalClassifications": [
                            tender["items"][0]["additionalClassifications"][0] for i in range(3)
                        ]
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [{"additionalClassifications": tender["items"][0]["additionalClassifications"]}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"enquiryPeriod": {
            "startDate": calculate_tender_business_date(
                parse_date(new_dateModified2), -timedelta(3), None, True
            ).isoformat(),
            "endDate": new_dateModified2
        }}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {u"description": {u"valueAddedTaxIncluded": u"Rogue field"}, u"location": u"body", u"name": u"guarantee"},
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"guarantee": {"amount": 12}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"guarantee": {"currency": "USD"}}}
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
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"NBUdiscountRate"}],
    )

    data = deepcopy(self.initial_data)
    del data["milestones"]
    data.update({"id": "hash", "doc_id": "hash2", "tenderID": "hash3", "NBUdiscountRate": 0.22986})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["NBUdiscountRate"], 0.22986)
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    if "noticePublicationDate" in tender:
        tender.pop("noticePublicationDate")
    self.assertEqual(
        set(tender),
        set(
            [
                u"procurementMethodType",
                u"id",
                u"dateModified",
                u"tenderID",
                u"status",
                u"enquiryPeriod",
                u"tenderPeriod",
                u"auctionPeriod",
                u"complaintPeriod",
                u"items",
                u"minValue",
                u"owner",
                u"minimalStepPercentage",
                u"procuringEntity",
                u"next_check",
                u"procurementMethod",
                u"awardCriteria",
                u"submissionMethod",
                u"title",
                u"title_en",
                u"date",
                u"NBUdiscountRate",
                u"fundingKind",
                u"yearlyPaymentsPercentageRange",
                u"mainProcurementCategory",
            ]
        ),
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"NBUdiscountRate": 1.2}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Value should be less than 0.99."], u"location": u"body", u"name": u"NBUdiscountRate"}],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"NBUdiscountRate": -2}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Value should be greater than 0."], u"location": u"body", u"name": u"NBUdiscountRate"}],
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
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Item id should be uniq for all items"], u"location": u"body", u"name": u"items"}],
    )
    data["items"][0]["id"] = "0"
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "lot",
            "title": u"Потужність всмоктування",
            "enum": [{"value": 0.1, "title": u"До 1000 Вт"}, {"value": 0.15, "title": u"Більше 1000 Вт"}],
        }
    ]
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"relatedItem": [u"This field is required."]}],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    data["features"][0]["relatedItem"] = "2"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"relatedItem": [u"relatedItem should be one of lots"]}],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    data["features"][0]["featureOf"] = "item"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"relatedItem": [u"relatedItem should be one of items"]}],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    data["features"][0]["relatedItem"] = "1"
    data["features"][0]["enum"][0]["value"] = 0.5
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"enum": [{u"value": [u"Float value should be less than 0.25."]}]}],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.15
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"enum": [u"Feature value should be uniq for feature"]}],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.1
    data["features"].append(data["features"][0].copy())
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Feature code should be uniq for all features"],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    data["features"][1]["code"] = u"OCDS-123454-YEARS"
    data["features"][1]["enum"][0]["value"] = 0.2
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Sum of max value of all features should be less then or equal to 25%"],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )


def tender_features(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = u"0440000000"
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": u"Потужність всмоктування",
            "title_en": u"Air Intake",
            "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.01, "title": u"До 1000 Вт"}, {"value": 0.04, "title": u"Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": u"Років на ринку",
            "title_en": u"Years trading",
            "description": u"Кількість років, які організація учасник працює на ринку",
            "enum": [{"value": 0.03, "title": u"До 3 років"}, {"value": 0.07, "title": u"Більше 3 років"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [{"value": 0.03, "title": u"До 90 днів"}, {"value": 0.07, "title": u"Більше 90 днів"}],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["features"], data["features"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"features": [{"featureOf": "tenderer", "relatedItem": None}, {}, {}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("features", response.json["data"])
    self.assertNotIn("relatedItem", response.json["data"]["features"][0])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"procuringEntity": {"contactPoint": {"faxNumber": None}}}},
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
            "title": u"Відстрочка платежу",
            "description": u"Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": u"До 90 днів"}, {"value": 0.1, "title": u"Більше 90 днів"}],
        }
    ]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

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
                u"location": u"body",
                u"name": u"value",
                u"description": {
                    u"contractDuration": [u"This field is required."],
                    u"annualCostsReduction": [u"This field is required."],
                    u"yearlyPaymentsPercentage": [u"This field is required."],
                },
            }
        ],
    )

    response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"features": [{"code": "OCDS-123-POSTPONEMENT"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["features"][0]["code"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"parameters": [{"code": "OCDS-123-POSTPONEMENT"}], "status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["parameters"][0]["code"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"features": [{"enum": [{"value": 0.2}]}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(0.2, response.json["data"]["features"][0]["enum"][0]["value"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"parameters": [{"value": 0.2}], "status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["parameters"][0]["code"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"features": []}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("features", response.json["data"])

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def create_tender_generated(self):
    data = self.initial_data.copy()
    del data["milestones"]
    # del data['awardPeriod']
    data.update({"id": "hash", "doc_id": "hash2", "tenderID": "hash3"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    if "noticePublicationDate" in tender:
        tender.pop("noticePublicationDate")
    self.assertEqual(
        set(tender),
        set(
            [
                u"procurementMethodType",
                u"id",
                u"dateModified",
                u"tenderID",
                u"status",
                u"enquiryPeriod",
                u"tenderPeriod",
                u"auctionPeriod",
                u"complaintPeriod",
                u"items",
                u"minValue",
                u"owner",
                u"minimalStepPercentage",
                u"procuringEntity",
                u"next_check",
                u"procurementMethod",
                u"NBUdiscountRate",
                u"awardCriteria",
                u"submissionMethod",
                u"title",
                u"title_en",
                u"date",
                u"fundingKind",
                u"yearlyPaymentsPercentageRange",
                u"mainProcurementCategory",
            ]
        ),
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])
