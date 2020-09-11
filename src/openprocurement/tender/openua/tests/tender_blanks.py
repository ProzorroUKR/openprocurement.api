# -*- coding: utf-8 -*-
from datetime import timedelta
from copy import deepcopy

from iso8601 import parse_date

from openprocurement.api.models import get_now
from openprocurement.api.constants import (
    SANDBOX_MODE,
    CPV_ITEMS_CLASS_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
)

from openprocurement.tender.belowthreshold.tests.base import test_organization, test_lots
from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.core.utils import calculate_tender_business_date

from openprocurement.tender.openua.models import Tender

# Tender UA Test


def simple_add_tender(self):
    u = Tender(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "aboveThresholdUA"

    u.delete_instance(self.db)


# TenderUAResourceTest


def empty_listing(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn("callback({", response.body)
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/tenders?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body)
    self.assertIn("callback({", response.body)

    response = self.app.get("/tenders?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)
    self.assertNotIn("callback({", response.body)

    response = self.app.get("/tenders?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body)
    self.assertIn("callback({", response.body)

    response = self.app.get("/tenders?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])

    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/tenders?feed=changes&offset=0", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Offset expired/invalid", u"location": u"params", u"name": u"offset"}],
    )

    response = self.app.get("/tenders?feed=changes&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])


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
        request_path,
        {"data": {"procurementMethodType": "aboveThresholdUA", "invalid_field": "invalid_value"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "aboveThresholdUA", "value": "invalid_value"}}, status=422
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
                u"name": u"value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "aboveThresholdUA", "procurementMethod": "invalid_value"}},
        status=422,
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
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"minimalStep"},
        response.json["errors"],
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"value"}, response.json["errors"]
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "aboveThresholdUA", "enquiryPeriod": {"endDate": "invalid_value"}}},
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
        {
            "data": {
                "procurementMethodType": "aboveThresholdUA",
                "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"},
            }
        },
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
        "startDate": (now + timedelta(days=16)).isoformat(),
        "endDate": (now + timedelta(days=16)).isoformat(),
    }
    self.initial_data["awardPeriod"] = {
        "startDate": (now + timedelta(days=15)).isoformat(),
        "endDate": (now + timedelta(days=15)).isoformat(),
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

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "1000.0"}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"value should be less than value of tender"],
                u"location": u"body",
                u"name": u"minimalStep",
            }
        ],
    )

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "100.0", "valueAddedTaxIncluded": False}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    u"valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender"
                ],
                u"location": u"body",
                u"name": u"minimalStep",
            }
        ],
    )

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "100.0", "currency": "USD"}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"currency should be identical to currency of value of tender"],
                u"location": u"body",
                u"name": u"minimalStep",
            }
        ],
    )

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

    data = test_organization["contactPoint"]["telephone"]
    del test_organization["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    test_organization["contactPoint"]["telephone"] = data
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

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]["endDate"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"deliveryDate": {u"endDate": [u"This field is required."]}}],
                u"location": u"body",
                u"name": u"items",
            }
        ],
    )


def create_tender_generated(self):
    data = self.initial_data.copy()
    # del data['awardPeriod']
    data.update({"id": "hash", "doc_id": "hash2", "tenderID": "hash3"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
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
                u"complaintPeriod",
                u"minimalStep",
                u"items",
                u"value",
                u"procuringEntity",
                u"next_check",
                u"procurementMethod",
                u"awardCriteria",
                u"submissionMethod",
                u"auctionPeriod",
                u"title",
                u"owner",
                u"date",
                u"mainProcurementCategory",
                u"milestones",
            ]
        ),
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.tender_id = tender["id"]
    tender_set = set(tender)
    if "procurementMethodDetails" in tender_set:
        tender_set.remove("procurementMethodDetails")
    self.assertEqual(
        tender_set - set(self.initial_data),
        {
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
        },
    )
    self.assertIn(tender["id"], response.headers["Location"])

    self.set_status("complete")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")
    expected_keys = {
        "id",
        "dateModified",
        "enquiryPeriod",
        "auctionPeriod",
        "complaintPeriod",
        "tenderID",
        "status",
        "procurementMethod",
        "awardCriteria",
        "submissionMethod",
        "owner",
        "date",
        "numberOfBids",
        "awardPeriod",
    }
    self.assertEqual(set(tender.keys()) - set(self.initial_data.keys()), expected_keys)


def patch_draft_invalid_json(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    response = self.app.patch(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), "{}d", content_type="application/json", status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Extra data: line 1 column 3 - line 1 column 4 (char 2 - 3)",
            }
        ],
    )


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    first_date = tender["date"]
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], first_date)
    self.assertNotEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procuringEntity": {"kind": "defense"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["procuringEntity"]["kind"], "defense")

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
            "description": ["tenderPeriod must be at least 15 full calendar days long"]
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
        {"data": {"items": [{"classification": {"scheme": "ДК021", "id": "44620000-2", "description": "Cartons 2"}}]}},
        status=200,
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [
                    {
                        "classification": {
                            "scheme": "ДК021",
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
    self.assertEqual(response.json["errors"][0]["description"], "Can't change classification")

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
    self.assertEqual(response.json["errors"][0]["description"], "Can't change enquiryPeriod")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def patch_tender_period(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")
    self.tender_id = tender["id"]
    self.set_enquiry_period_end()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"description": "new description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 7 days")
    tender_period_end_date = calculate_tender_business_date(
        get_now(), timedelta(days=7), tender
    ) + timedelta(seconds=10)
    enquiry_period_end_date = calculate_tender_business_date(
        tender_period_end_date, -timedelta(days=10), tender
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"description": "new description", "tenderPeriod": {"endDate": tender_period_end_date.isoformat()}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())


# TenderUAProcessTest


def invalid_bid_tender_features(self):
    self.app.authorization = ("Basic", ("broker", ""))
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
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["parameters"] = [{"code": "OCDS-123454-POSTPONEMENT", "value": 0.1}]
    bid_data["value"] = {"amount": 500}
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
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
        {"data": {"parameters": [{"code": "OCDS-123-POSTPONEMENT"}], "status": "active"}},
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
        {"data": {"parameters": [{"value": 0.2}], "status": "active"}},
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

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def invalid_bid_tender_lot(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    lots = []
    for lot in test_lots * 2:
        response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": lot})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lots.append(response.json["data"]["id"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update({
        "status": "draft",
        "lotValues": [{"value": {"amount": 500}, "relatedLot": i} for i in lots]
    })
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(tender_id, lots[0], owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def one_valid_bid_tender_ua(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering XXX temporary action.
    response = self.set_status(
        "active.tendering", {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
    )
    self.assertIn("auctionPeriod", response.json["data"])

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    bid_id = self.bid_id = response.json["data"]["id"]

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def invalid1_and_1draft_bids_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    bid_data["status"] = "draft"
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def activate_bid_after_adding_lot(self):
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, owner_token), {"data": test_lots[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot_id = response.json["data"]["id"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))

    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"status": "active", "value": None, "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}]}},
    )

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))

    self.assertNotIn("value", response.json)
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 450}
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data["value"] = {"amount": 475}
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.auction
    self.set_status("active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction".format(tender_id),
        {
            "data": {
                "auctionUrl": "https://tender.auction.url",
                "bids": [
                    {"id": i["id"], "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"])}
                    for i in auction_bids_data
                ],
            }
        },
    )
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json["data"]["participationUrl"], "https://tender.auction.url/for_bid/{}".format(bid_id))

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(tender_id), {"data": {"bids": auction_bids_data}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    # create first award complaint
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]
    # create tender contract document for test
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender_id, contract_id, owner_token),
        upload_files=[("file", "name.doc", "content")],
        status=201,
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender_id, contract_id, owner_token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(tender_id, contract_id, doc_id, owner_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(tender_id, contract_id, doc_id, owner_token),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def lost_contract_for_active_award(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 450}
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # create bid #2
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.auction
    self.set_status("active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(tender_id), {"data": {"bids": auction_bids_data}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # lost contract
    tender = self.db.get(tender_id)
    tender["contracts"] = None
    self.db.save(tender)
    # check tender
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertNotIn("contracts", response.json["data"])
    self.assertIn("next_check", response.json["data"])
    # create lost contract
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contracts", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    contract_id = response.json["data"]["contracts"][-1]["id"]
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


# TenderUAResourceTest


def tender_with_main_procurement_category(self):
    data = dict(**self.initial_data)

    # test fail creation
    data["mainProcurementCategory"] = "whiskey,tango,foxtrot"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "mainProcurementCategory",
                "description": ["Value must be one of ['goods', 'services', 'works']."],
            }
        ],
    )

    # test success creation
    data["mainProcurementCategory"] = "goods"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "goods")

    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update tender in active.tendering status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "services"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")


def tender_finance_milestones(self):
    data = dict(**self.initial_data)

    # test creation
    data["milestones"] = [
        {
            "id": "a" * 32,
            "title": "signingTheContract",
            "code": "prepayment",
            "type": "financing",
            "duration": {"days": 2, "type": "banking"},
            "sequenceNumber": 0,
            "percentage": 45.55,
        },
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 999, "type": "calendar"},
            "sequenceNumber": 0,
            "percentage": 54.45,
        },
    ]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertIn("milestones", tender)
    self.assertEqual(len(tender["milestones"]), 2)
    for milestone in tender["milestones"]:
        self.assertEqual(
            set(milestone.keys()), {"id", "code", "duration", "percentage", "type", "sequenceNumber", "title"}
        )
    self.assertEqual(data["milestones"][0]["id"], tender["milestones"][0]["id"])
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update
    new_title = "endDateOfTheReportingPeriod"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"milestones": [{}, {"title": new_title}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("milestones", response.json["data"])
    milestones = response.json["data"]["milestones"]
    self.assertEqual(len(milestones), 2)
    self.assertEqual(milestones[0]["title"], tender["milestones"][0]["title"])
    self.assertEqual(milestones[1]["title"], new_title)
