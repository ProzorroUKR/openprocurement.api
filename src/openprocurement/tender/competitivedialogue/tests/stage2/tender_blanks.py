# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import (
    SANDBOX_MODE,
    CPV_ITEMS_CLASS_FROM,
    ROUTE_PREFIX,
    RELEASE_2020_04_19,
)
from openprocurement.api.utils import get_now

from openprocurement.tender.core.tests.cancellation import activate_cancellation_with_complaints_after_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_cancellation
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central as create_tender_central_base,
)

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE2_STATUS,
    CD_UA_TYPE,
    CD_EU_TYPE,
)
from openprocurement.tender.competitivedialogue.models import TenderStage2EU, TenderStage2UA
from openprocurement.tender.core.tests.criteria_utils import add_criteria


# CompetitiveDialogStage2Test
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.core.utils import calculate_tender_business_date


def simple_add_cd_tender_eu(self):
    u = TenderStage2EU(self.test_tender_data_eu)
    u.tenderID = "EU-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == STAGE_2_EU_TYPE

    u.delete_instance(self.db)


def simple_add_cd_tender_ua(self):
    u = TenderStage2UA(self.test_tender_data_ua)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == STAGE_2_UA_TYPE

    u.delete_instance(self.db)


# CompetitiveDialogStage2EUResourceTest
def create_tender_invalid_eu(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
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

    self.app.authorization = ("Basic", ("competitive_dialogue", ""))

    self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "invalid_field": "invalid_value"}}, status=403
    )
    self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "value": "invalid_value"}}, status=403
    )
    self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "procurementMethod": "invalid_value"}}, status=403
    )
    self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": CD_EU_TYPE, "enquiryPeriod": {"endDate": "invalid_value"}}},
        status=403,
    )
    self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": CD_EU_TYPE, "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"}}},
        status=403,
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

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "6674850281.0"}
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

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [{u"deliveryDate": [u"This field is required."]}], u"location": u"body", u"name": u"items"}],
    )


def patch_tender_eu(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.set_enquiry_period_end()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"value": {"amount": 501, "currency": u"UAH"}}},
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
        {
            "data": {
                "value": {"amount": 502, "currency": u"UAH"},
                "tenderPeriod": {"endDate": tender_period_end_date.isoformat()},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())
    self.assertNotEqual(response.json["data"]["value"]["amount"], 502)
    self.assertNotEqual(response.json["data"]["value"]["amount"], 501)

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
    self.assertNotIn("guarantee", response.json["data"])


# TenderStage2UAResourceTest
def empty_listing_ua(self):
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


def create_tender_invalid_ua(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
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
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "invalid_field": "invalid_value"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "value": "invalid_value"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "procurementMethod": "invalid_value"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": CD_UA_TYPE, "enquiryPeriod": {"endDate": "invalid_value"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": CD_UA_TYPE, "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

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


def patch_tender_ua(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.set_status("active.tendering")
    self.set_enquiry_period_end()
    self.app.get("/tenders/{}?acc_token={}".format(tender["id"], owner_token))
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"value": {"amount": 501, "currency": u"UAH"}}},
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
        {
            "data": {
                "value": {"amount": 501, "currency": u"UAH"},
                "tenderPeriod": {"endDate": tender_period_end_date.isoformat()},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())

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
    self.assertNotIn("guarantee", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"currency": "USD", "amount": 300}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("guarantee", response.json["data"])


# CompetitiveDialogStage2ResourceTest
def listing(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    tokens = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json("/tenders", {"data": self.test_tender_data_eu})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tenders.append(response.json["data"])
        tokens.append(response.json["access"]["token"])

    # set status to draft.stage2
    for tender in tenders:
        self.set_tender_status(tender, tokens[tenders.index(tender)], "draft.stage2")

    # set status to active.tendering
    for tender in tenders:
        offset = get_now().isoformat()
        add_criteria(self, tender["id"], tokens[tenders.index(tender)])
        response = self.set_tender_status(tender, tokens[tenders.index(tender)], "active.tendering")
        tenders[tenders.index(tender)] = response.json["data"]

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))

    while True:
        response = self.app.get("/tenders?offset={}".format(offset))
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/tenders", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders], reverse=True)
    )

    response = self.app.get("/tenders?descending=1&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    test_tender_stage2_data_ua2 = self.test_tender_data_eu.copy()
    test_tender_stage2_data_ua2["mode"] = "test"
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": test_tender_stage2_data_ua2})
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "draft.stage2")
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "active.tendering")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/tenders?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_draft(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    data = self.test_tender_data_eu.copy()
    data.update({"status": "draft"})

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.test_tender_data_eu})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.set_tender_status(response.json["data"], response.json["access"]["token"], "draft.stage2")
        response = self.set_tender_status(response.json["data"], response.json["access"]["token"], "active.tendering")
        tenders.append(response.json["data"])
        response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))


def tender_not_found(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/tenders/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.patch_json("/tenders/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def invalid_procurementMethod(self):
    """ Create create or edit field procurementMethod second stage """
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    data = deepcopy(self.initial_data)
    del data["procurementMethod"]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(response.json["data"]["procurementMethod"], "selective")

    add_criteria(self, tender["id"], token)
    # Try edit
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"procurementMethod": "open", "status": "active.tendering"}},
    )
    self.assertEqual(response.json["data"]["procurementMethod"], "selective")

    # Try create and send wrong procurementMethod
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    data["procurementMethod"] = "open"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procurementMethod"], "selective")


def listing_changes(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    tokens = []

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        token = response.json["access"]["token"]
        data = response.json["data"]
        self.set_tender_status(data, token, "draft.stage2")
        data = self.set_tender_status(data, token, "active.tendering").json["data"]
        tenders.append(data)
        tokens.append(token)

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))

    response = self.app.get("/tenders?feed=changes&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders], reverse=True)
    )

    response = self.app.get("/tenders?feed=changes&descending=1&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    test_tender_stage2_data_eu2 = self.initial_data.copy()
    test_tender_stage2_data_eu2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_stage2_data_eu2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "draft.stage2")
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "active.tendering")

    while True:
        response = self.app.get("/tenders?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def create_tender(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)
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
                u"complaintPeriod",
                u"tenderID",
                u"awardCriteria",
                u"submissionMethod",
                u"date",
            ]
        ),
    )
    self.assertIn(tender["id"], response.headers["Location"])

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set(tender))
    self.assertEqual(response.json["data"], tender)

    response = self.app.post_json("/tenders?opt_jsonp=callback", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"', response.body)

    response = self.app.post_json("/tenders?opt_pretty=1", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)

    tender_data = deepcopy(self.initial_data)
    tender_data["guarantee"] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    data = response.json["data"]
    self.assertIn("guarantee", data)
    self.assertEqual(data["guarantee"]["amount"], 100500)
    self.assertEqual(data["guarantee"]["currency"], "USD")


def tender_funders(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["funders"] = [deepcopy(test_organization)]
    tender_data["funders"][0]["identifier"]["id"] = "44000"
    tender_data["funders"][0]["identifier"]["scheme"] = "XM-DAC"
    del tender_data["funders"][0]["scale"]
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["id"], "44000")
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["scheme"], "XM-DAC")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    tender_data["funders"].append(deepcopy(test_organization))
    tender_data["funders"][1]["identifier"]["id"] = "44000"
    tender_data["funders"][1]["identifier"]["scheme"] = "XM-DAC"
    del tender_data["funders"][1]["scale"]
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Funders' identifier should be unique"], u"location": u"body", u"name": u"funders"}],
    )

    tender_data["funders"][0]["identifier"]["id"] = "some id"
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Funder identifier should be one of the values allowed"],
                u"location": u"body",
                u"name": u"funders",
            }
        ],
    )

    # Can't test different funders for now 'cause we have only one funder in list
    # tender_data['funders'][0]['identifier']['id'] = '11111111'
    # response = self.app.post_json('/tenders', {'data': tender_data})
    # self.assertEqual(response.status, '201 Created')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)


def tender_features_invalid(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
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
            "enum": [
                {"value": 0.1, "title": u"До 1000 Вт"},
                {"value": 0.15, "title": u"Більше 1000 Вт"},
                {"value": 0.3, "title": u"До 500 Вт"},
            ],
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
    data["features"][0]["enum"][0]["value"] = 1.0
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"enum": [{u"value": [u"Float value should be less than 0.99."]}]}],
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
    copy_data = deepcopy(data)
    copy_data["features"][1]["code"] = u"OCDS-123454-YEARS"
    copy_data["features"][1]["enum"][0]["value"] = 0.5
    feature = deepcopy(copy_data["features"][1])
    feature["code"] = u"OCDS-123455-YEARS"
    copy_data["features"].append(feature)
    feature = deepcopy(copy_data["features"][1])
    feature["code"] = u"OCDS-123456-YEARS"
    copy_data["features"].append(feature)
    response = self.app.post_json("/tenders", {"data": copy_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Sum of max value of all features should be less then or equal to 99%"],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )
    del copy_data
    del feature


def get_tender(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], tender)

    response = self.app.get("/tenders/{}?opt_jsonp=callback".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get("/tenders/{}?opt_pretty=1".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body)


def tender_features(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    data = self.initial_data.copy()
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
            "enum": [{"value": 0.05, "title": u"До 1000 Вт"}, {"value": 0.1, "title": u"Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": u"Років на ринку",
            "title_en": u"Years trading",
            "description": u"Кількість років, які організація учасник працює на ринку",
            "enum": [{"value": 0.05, "title": u"До 3 років"}, {"value": 0.1, "title": u"Більше 3 років"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "title_en": u"Postponement of payment",
            "description": u"Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": u"До 90 днів"}, {"value": 0.1, "title": u"Більше 90 днів"}],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["features"], data["features"])
    token = response.json["access"]["token"]
    self.tender_id = response.json["data"]["id"]
    # switch to draft.stage2
    self.set_status(STAGE2_STATUS)
    response = self.app.get("/tenders/{}?acc_token={}".format(tender["id"], token))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("features", response.json["data"])


def patch_tender_1(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft")
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.set_status(STAGE2_STATUS)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/credentials?acc_token={}".format(tender["id"], owner_token), {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/credentials?acc_token={}".format(tender["id"], self.test_access_token_data), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")

    owner_token = response.json["access"]["token"]

    # switch to active.tendering
    self.set_status("active.tendering")
    tender["status"] = "active.tendering"

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
    self.assertNotIn("guarantee", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 100, "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("guarantee", response.json["data"])

    deliveryDateStart = (get_now() + timedelta(days=10)).isoformat()
    deliveryDateEnd = (get_now() + timedelta(days=15)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [
                    {
                        "description": u"Шолом Дарта Вейдера",
                        "unit": {"name": u"item", "code": u"99999999-9"},
                        "quantity": 3,
                        "deliveryDate": {"startDate": deliveryDateStart, "endDate": deliveryDateEnd},
                        "deliveryAddress": {
                            "countryName": "Україна",
                            "postalCode": "49000",
                            "region": "Дніпропетровська область",
                            "locality": "м. Дніпро",
                            "streetAddress": "вул. Нютона 4",
                        },
                    }
                ]
            }
        },
    )
    self.assertNotEqual(response.json["data"]["items"][0]["description"], u"Шолом Дарта Вейдера")
    self.assertNotEqual(response.json["data"]["items"][0]["unit"]["code"], u"99999999-9")
    self.assertNotEqual(response.json["data"]["items"][0]["quantity"], 3)
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["startDate"], deliveryDateStart)
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["endDate"], deliveryDateEnd)
    self.assertNotEqual(response.json["data"]["items"][0]["deliveryAddress"]["countryName"], u"УКРАЇНА")
    self.assertNotEqual(response.json["data"]["items"][0]["deliveryAddress"]["postalCode"], u"49000")
    self.assertNotEqual(response.json["data"]["items"][0]["deliveryAddress"]["region"], u"Дніпропетровська область")
    self.assertNotEqual(response.json["data"]["items"][0]["deliveryAddress"]["locality"], u"м. Дніпро")
    self.assertNotEqual(response.json["data"]["items"][0]["deliveryAddress"]["streetAddress"], u"вул. Нютона 4")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def dateModified_tender(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")

    self.tender_id = response.json["data"]["id"]
    # switch to active.tendering
    self.set_status("active.tendering")

    tender = response.json["data"]
    dateModified = tender["dateModified"]
    owner_token = response.json["access"]["token"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    tender = response.json["data"]
    dateModified = tender["dateModified"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], tender)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def guarantee(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    data = deepcopy(self.initial_data)
    data["guarantee"] = {"amount": 55}
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    # switch to active.tendering
    self.set_status("active.tendering")

    owner_token = response.json["access"]["token"]
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"guarantee": {"amount": 70}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 55)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")


def tender_Administrator_change(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    self.set_tender_status(tender, response.json["access"]["token"], "draft.stage2")
    response = self.set_tender_status(tender, response.json["access"]["token"], "active.tendering")

    tender = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.db.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    self.test_bids_data[0]["tenderers"][0]["identifier"]["id"] = identifier["id"]
    self.test_bids_data[0]["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    response = self.app.post_json(
        "/tenders/{}/questions".format(tender["id"]),
        {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}".format(tender["id"]),
        {"data": {"mode": u"test", "procuringEntity": {"identifier": {"id": "00000000"}}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], u"test")
    self.assertEqual(response.json["data"]["procuringEntity"]["identifier"]["id"], "00000000")

    response = self.app.patch_json(
        "/tenders/{}/questions/{}".format(tender["id"], question["id"]), {"data": {"answer": "answer"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"], [{"location": "url", "name": "role", "description": "Forbidden"}])

    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id = tender["id"]
    owner_token = self.tender_token = response.json["access"]["token"]

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender["id"], owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"mode": u"test"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], u"test")


def patch_not_author(self):
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_tender_status(tender, response.json["access"]["token"], "draft.stage2")
    response = self.set_tender_status(tender, response.json["access"]["token"], "active.tendering")

    tender = response.json["data"]

    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post(
        "/tenders/{}/documents".format(tender["id"]), upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(tender["id"], doc_id, owner_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")


# TenderStage2UAProcessTest
def invalid_tender_conditions(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # cancellation
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(
            self, cancellation_id, tender_id, owner_token)
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_valid_bid_tender_ua(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    self.app.authorization = ("Basic", ("broker", ""))
    # switch to active.tendering XXX temporary action.
    response = self.set_status(
        "active.tendering", {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
    )
    self.assertIn("auctionPeriod", response.json["data"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.db.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["tenderers"][0]["identifier"]["id"] = identifier["id"]
    bid_data["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    bid_data["value"] = {"amount": 500}

    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def one_invalid_and_1draft_bids_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua})
    tender = response.json["data"]
    tender_id = self.tender_id = tender["id"]
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.db.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["tenderers"][0]["identifier"]["id"] = identifier["id"]
    bid_data["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    bid_data["value"] = {"amount": 500}
    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    bid_data["status"] = "draft"
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
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
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua})
    tender = response.json["data"]
    tender_id = self.tender_id = tender["id"]
    owner_token = response.json["access"]["token"]
    self.set_status("active.tendering")
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.db.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["tenderers"][0]["identifier"]["id"] = identifier["id"]
    bid_data["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    bid_data["value"] =  {"amount": 450}

    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    # create second bid
    bid_data["value"] = {"amount": 475}

    self.app.authorization = ("Basic", ("broker", ""))
    self.app.post_json(
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
    self.app.patch_json(
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
    self.app.post_json("/tenders/{}/auction".format(tender_id), {"data": {"bids": auction_bids_data}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
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


def tender_milestones_not_required(self):
    data = dict(**self.initial_data)
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    data["milestones"] = []

    self.app.post_json("/tenders", {"data": data}, status=201)



def create_tender_central(self):
    with change_auth(self.app, ("Basic", ("competitive_dialogue", ""))):
        create_tender_central_base(self)
