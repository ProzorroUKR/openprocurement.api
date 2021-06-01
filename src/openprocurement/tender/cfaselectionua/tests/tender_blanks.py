# -*- coding: utf-8 -*-
import jmespath
import mock
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now, parse_date
from openprocurement.api.constants import (
    ROUTE_PREFIX,
    SANDBOX_MODE,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    CPV_ITEMS_CLASS_FROM,
)
from openprocurement.tender.belowthreshold.tests.base import test_claim, test_cancellation
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import activate_cancellation_without_complaints_after_2020_04_19
from openprocurement.tender.cfaselectionua.constants import (
    BOT_NAME,
    ENQUIRY_PERIOD,
    MIN_PERIOD_UNTIL_AGREEMENT_END,
    MIN_ACTIVE_CONTRACTS,
    AGREEMENT_IDENTIFIER,
    TENDERING_DURATION,
)
from openprocurement.tender.cfaselectionua.tests.base import test_organization, test_features
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.belowthreshold.tests.tender_blanks import create_tender_with_earlier_non_required_unit


# TenderResourceTest


def listing(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    data = deepcopy(self.initial_data)
    data["agreements"] = [{"id": uuid4().hex}]
    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "draft.pending"}},
        )
        tenders.append(response.json["data"])

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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

    test_tender_data2 = data.copy()
    test_tender_data2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
        {"data": {"status": "draft.pending"}},
    )

    while True:
        response = self.app.get("/tenders?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


@mock.patch(
    "openprocurement.tender.cfaselectionua.models.submodels.item.UNIT_PRICE_REQUIRED_FROM", get_now() + timedelta(days=1))
def create_cfaselectionua_tender_with_earlier_non_required_unit(self):
    create_tender_with_earlier_non_required_unit(self)


def create_tender_with_required_unit(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)
    tender_data = deepcopy(self.initial_data)

    _unit = tender_data["items"][0].pop("unit")
    _quantity = tender_data["items"][0].pop("quantity")
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    {
                        'unit': ['This field is required.'],
                        'quantity': ['This field is required.']
                    }
                ],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['quantity'] = _quantity
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [{'unit': ['This field is required.']}],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['unit'] = _unit
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("quantity", response.json["data"]['items'][0])
    self.assertIn("unit", response.json["data"]['items'][0])

    _unit_code = tender_data["items"][0]["unit"].pop("code")
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [{'unit': {'code': ['This field is required.']}}],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['unit']['code'] = _unit_code
    tender_data["items"][0]['unit']['value'] = {
        "currency": "USD",
        "valueAddedTaxIncluded": False
    }
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json['errors'],
        [
            {
                'description': [
                    {'unit': {'value': {'amount': ['This field is required.']}}}
                ],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['unit']['value']['amount'] = 100
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    resp = response.json["data"]
    self.assertEqual('USD', resp["items"][0]['unit']['value']['currency'])
    self.assertEqual(False, resp["items"][0]['unit']['value']['valueAddedTaxIncluded'])

    tender_data["items"][0]["unit"]["code"] = "unknown_code"
    response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json['errors'],
        [
            {
                'description': [
                    {u'unit': {u'code': [u'Code should be one of valid unit codes.']}}
                ],
                'location': 'body', 'name': 'items'
            }
        ]
    )

    tender_data["items"][0]["unit"]["code"] = "KGM"
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    resp = response.json["data"]
    self.assertEqual("KGM", resp["items"][0]["unit"]["code"])


def listing_changes(self):
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    data = deepcopy(self.initial_data)
    data["agreements"] = [{"id": uuid4().hex}]
    for i in range(3):
        response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "draft.pending"}},
        )
        tenders.append(response.json["data"])

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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

    test_tender_data2 = data.copy()
    test_tender_data2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
        {"data": {"status": "draft.pending"}},
    )

    while True:
        response = self.app.get("/tenders?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_draft(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    data = self.initial_data.copy()
    data.update({"status": "draft", "agreements": [{"id": uuid4().hex}]})

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "draft.pending"}},
        )
        tenders.append(response.json["data"])

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))


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
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": {"procurementMethodType": "invalid_value"}}, status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Not implemented", "location": "body", "name": "procurementMethodType"}],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "closeFrameworkAgreementSelectionUA", "invalid_field": "invalid_value"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "closeFrameworkAgreementSelectionUA", "value": "invalid_value"}},
        status=422,
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
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "closeFrameworkAgreementSelectionUA", "procurementMethod": "invalid_value"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": ["Value must be one of ['open', 'selective', 'limited']."],
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "procurementMethodType": "closeFrameworkAgreementSelectionUA",
                "enquiryPeriod": {"endDate": "invalid_value"},
            }
        },
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
        {
            "data": {
                "procurementMethodType": "closeFrameworkAgreementSelectionUA",
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
        [{"description": {"endDate": ["date value out of range"]}, "location": "body", "name": "enquiryPeriod"}],
    )

    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2014-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    del self.initial_data["tenderPeriod"]
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

    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2015-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data})
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("tenderPeriod", response.json["data"])

    del self.initial_data["tenderPeriod"]
    now = get_now()
    self.initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=201)
    del self.initial_data["awardPeriod"]
    self.initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=15)).isoformat(),
        "endDate": (now + timedelta(days=15)).isoformat(),
    }
    self.initial_data["awardPeriod"] = {
        "startDate": (now + timedelta(days=14)).isoformat(),
        "endDate": (now + timedelta(days=14)).isoformat(),
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
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status, "201 Created")
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

    data = test_organization["contactPoint"]["telephone"]
    del test_organization["contactPoint"]["telephone"]
    # response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    test_organization["contactPoint"]["telephone"] = data

    data = self.initial_data["items"][0].copy()
    data["id"] = uuid4().hex
    classification = data["classification"].copy()
    classification["id"] = "19212310-1"
    data["classification"] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(
            response.json["errors"],
            [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [{"description": ["CPV group of items be identical"], "location": "body", "name": "items"}],
        )

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "160173000-1"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertIn("Value must be one of [", response.json["errors"][0]["description"][0]["classification"]["id"][0])

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertIn("Value must be one of [", response.json["errors"][0]["description"][0]["classification"]["id"][0])
    data = deepcopy(self.initial_data)
    data["items"] = [data["items"][0]]
    data["items"][0]["classification"]["id"] = "33600000-6"
    del data["items"][0]["additionalClassifications"]

    procuringEntity = self.initial_data["procuringEntity"]
    data = self.initial_data["procuringEntity"].copy()
    del data["kind"]
    self.initial_data["procuringEntity"] = data
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=403)
    self.initial_data["procuringEntity"] = procuringEntity
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "'' procuringEntity cannot publish this type of procedure. Only authority, central, defense, general, other, social, special are allowed.",
                "location": "body",
                "name": "kind",
            }
        ],
    )


def create_tender_generated(self):
    data = deepcopy(self.initial_data)

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
        {
            "procurementMethodType",
            "id",
            "date",
            "dateModified",
            "tenderID",
            "status",
            "procuringEntity",
            "items",
            "procurementMethod",
            "awardCriteria",
            "submissionMethod",
            "title",
            "owner",
            "agreements",
            "lots",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])


def create_tender_draft(self):
    data = deepcopy(self.initial_data)
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.tender_id = tender["id"]
    self.tender_token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)


def create_tender_with_available_language(self):
    data = deepcopy(self.initial_data)
    data["procuringEntity"]["contactPoint"]["availableLanguage"] = "test"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "contactPoint": {"availableLanguage": ["Value must be one of ['uk', 'en', 'ru']."]}
                },
                "location": "body",
                "name": "procuringEntity",
            }
        ],
    )

    data["procuringEntity"]["contactPoint"]["availableLanguage"] = "uk"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"]["contactPoint"]["availableLanguage"], "uk")


def create_tender_with_value(self):
    data = deepcopy(self.initial_data)
    data.update({"status": "draft", "value": {"amount": 179511.28, "currency": "UAH", "valueAddedTaxIncluded": True}})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertNotIn("value", response.json["data"])


def create_tender_draft_pending(self):
    create_tender_draft(self)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "draft.pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "draft.pending")


def create_tender_draft_pending_without_features(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    data["features"] = self.initial_agreement_with_features["features"]

    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    tender = response.json["data"]
    self.tender_id = tender["id"]
    self.tender_token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")
    self.assertNotIn("features", tender)

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "draft.pending"}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotIn("features", response.json["data"])
    self.assertEqual(response.json["data"]["status"], "draft.pending")


def create_tender_from_terminated_agreement(self):
    agreement = deepcopy(self.initial_agreement)
    agreement["status"] = "terminated"
    agreement["terminationDetails"] = "Do not need this service anymore"
    agreement["id"] = self.agreement_id

    create_tender_draft_pending(self)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {
            "data": {
                "tenderers": [test_organization],
                "subcontractingDetails": "test_details",
                "lotValues": [
                    {
                        "subcontractingDetails": "test_details",
                        "value": {"amount": 500},
                        "relatedLot": self.initial_data["lots"][0]["id"],
                    }
                ],
            }
        },
        status=403,
    )
    self.assertEqual(response.status_code, 403)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add bid in current (draft.pending) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    self.app.authorization = ("Basic", (BOT_NAME, ""))

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"agreements": [agreement]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["agreements"][0]["status"], "terminated")
    self.assertEqual(tender["agreements"][0]["terminationDetails"], "Do not need this service anymore")
    self.assertEqual(tender["status"], "draft.pending")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.enquiries"}}
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["agreements"][0]["status"], "terminated")
    self.assertEqual(tender["status"], "draft.unsuccessful")
    self.assertEqual(tender["unsuccessfulReason"], ["agreements[0] status is not active"])
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.unsuccessful")
    self.assertEqual(tender["unsuccessfulReason"], ["agreements[0] status is not active"])


def create_tender_from_agreement_with_features(self):
    self.agreement = deepcopy(self.initial_agreement_with_features)
    create_tender_draft_pending(self)
    create_tender_draft_pending_without_features(self)
    create_tender_from_agreement_with_features_successful(self)


def create_tender_from_agreement_with_features_0_3(self):

    self.agreement = deepcopy(self.initial_agreement_with_features)
    self.agreement["features"] = [self.agreement["features"][0]]
    self.agreement["features"][0]["enum"] = [
        {"value": 0.0, "title": "До 1000 Вт"},
        {"value": 0.3, "title": "Більше 1000 Вт"},
    ]
    for contract in self.agreement["contracts"]:
        contract["parameters"] = [{"code": "OCDS-123454-AIR-INTAKE", "value": 0.3}]
    create_tender_draft_pending(self)
    create_tender_from_agreement_with_features_successful(self)


def create_tender_from_agreement_with_features_successful(self):
    self.app.authorization = ("Basic", (BOT_NAME, ""))

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"agreements": [self.agreement], "status": "active.enquiries"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["features"], self.agreement["features"])
    self.assertEqual(response.json["data"]["status"], "active.enquiries")

    self.app.authorization = ("Basic", ("broker", ""))


def create_tender_from_agreement_with_features_0_3_successful(self):
    self.app.authorization = ("Basic", (BOT_NAME, ""))

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"agreements": [], "status": "active.enquiries"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["features"], self.agreement["features"])
    self.assertEqual(response.json["data"]["status"], "active.enquiries")

    self.app.authorization = ("Basic", ("broker", ""))


def create_tender_from_agreement_with_changes(self):
    self.agreement = agreement = deepcopy(self.initial_agreement)
    now = get_now().isoformat()
    agreement["changes"] = [
        {
            "modifications": [{"itemId": agreement["items"][0]["id"], "addend": 0.9}],
            "rationaleType": "taxRate",
            "dateSigned": now,
            "rationale": "text",
            "date": now,
            "id": uuid4().hex,
        }
    ]
    agreement["id"] = self.agreement_id

    create_tender_draft_pending(self)
    create_tender_from_agreement_with_active_changes(self)
    create_tender_draft_pending(self)
    create_tender_from_agreement_with_pending_changes(self)


def create_tender_from_agreement_with_invalid_changes(self):
    self.agreement = agreement = deepcopy(self.initial_agreement)
    now = get_now().isoformat()
    agreement["changes"] = [
        {
            "modifications": [{"itemId": agreement["items"][0]["id"], "addend": 0.9}],
            "rationaleType": "InvalidRationalType",
            "dateSigned": now,
            "rationale": "text",
            "date": now,
            "id": uuid4().hex,
        }
    ]
    agreement["id"] = self.agreement_id
    create_tender_draft_pending(self)

    self.app.authorization = ("Basic", (BOT_NAME, ""))

    self.agreement["changes"][0]["status"] = "active"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"agreements": [self.agreement], "status": "active.enquiries"}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        {
            'location': 'body', 'name': 'agreements',
            'description': {
                'changes': ['Input for polymorphic field did not match any model']
            }
        },
        response.json["errors"][0]
    )


def create_tender_from_agreement_with_active_changes(self):
    self.app.authorization = ("Basic", (BOT_NAME, ""))

    self.agreement["changes"][0]["status"] = "active"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"agreements": [self.agreement], "status": "active.enquiries"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("changes", response.json["data"]["agreements"][0])
    self.assertEqual(response.json["data"]["status"], "active.enquiries")

    self.app.authorization = ("Basic", ("broker", ""))


def create_tender_from_agreement_with_pending_changes(self):
    self.app.authorization = ("Basic", (BOT_NAME, ""))

    self.agreement["changes"][0]["status"] = "pending"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"agreements": [self.agreement], "status": "active.enquiries"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("changes", response.json["data"]["agreements"][0])
    self.assertEqual(response.json["data"]["status"], "draft.unsuccessful")
    self.assertEqual(response.json["data"]["unsuccessfulReason"], ["agreements[0] has pending change"])

    self.app.authorization = ("Basic", ("broker", ""))


def create_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    self.initial_data["agreements"] = [{"id": self.agreement_id}]
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertEqual(response.json["data"]["agreements"][0]["id"], self.agreement_id)
    tender = response.json["data"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set(tender))

    response = self.app.post_json("/tenders?opt_jsonp=callback", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"', response.body.decode())

    response = self.app.post_json("/tenders?opt_pretty=1", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    response = self.app.post_json("/tenders", {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    data = deepcopy(self.initial_data)
    data["minimalStep"] = {"amount": 35, "currency": "UAH"}
    del data["items"][0]["deliveryAddress"]["postalCode"]
    del data["items"][0]["deliveryAddress"]["locality"]
    del data["items"][0]["deliveryAddress"]["streetAddress"]
    del data["items"][0]["deliveryAddress"]["region"]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    self.assertNotIn("minimalStep", response.json["data"])  # minimalStep cannot be created
    self.assertNotIn("postalCode", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("locality", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("streetAddress", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("region", response.json["data"]["items"][0]["deliveryAddress"])

    data = deepcopy(self.initial_data)
    data["lots"][0]["minimalStep"] = {"amount": 35, "currency": "UAH"}
    data["items"] = [data["items"][0]]
    data["items"][0]["classification"]["id"] = "33600000-6"

    additional_classification_0 = {
        "scheme": "INN",
        "id": "sodium oxybate",
        "description": "папір і картон гофровані, паперова й картонна тара",
    }
    data["items"][0]["additionalClassifications"] = [additional_classification_0]

    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["id"], "33600000-6")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["scheme"], "ДК021")
    self.assertEqual(response.json["data"]["items"][0]["additionalClassifications"][0], additional_classification_0)
    self.assertNotIn("minimalStep", response.json["data"]["lots"][0])

    additional_classification_1 = {
        "scheme": "ATC",
        "id": "A02AF",
        "description": "папір і картон гофровані, паперова й картонна тара",
    }
    data["items"][0]["additionalClassifications"].append(additional_classification_1)
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["id"], "33600000-6")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["scheme"], "ДК021")
    self.assertEqual(
        response.json["data"]["items"][0]["additionalClassifications"],
        [additional_classification_0, additional_classification_1],
    )

    tender_data = deepcopy(self.initial_data)
    tender_data["guarantee"] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    data = response.json["data"]
    self.assertIn("guarantee", data)
    self.assertEqual(data["guarantee"]["amount"], 100500)
    self.assertEqual(data["guarantee"]["currency"], "USD")

    tender_data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))


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
    self.tender_id = tender["id"]
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
        [{"description": ["Funders' identifier should be unique"], "location": "body", "name": "funders"}],
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
                "description": ["Funder identifier should be one of the values allowed"],
                "location": "body",
                "name": "funders",
            }
        ],
    )
    # tender_data['funders'][0]['identifier']['id'] = '11111111'
    # response = self.app.post_json('/tenders', {'data': tender_data})
    # self.assertEqual(response.status, '201 Created')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)
    # tender = response.json['data']
    # token = response.json['access']['token']

    # response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'funders': [{
    #     "identifier": {'id': '22222222'}}, {}]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)
    # self.assertEqual(response.json['data']['funders'][0]['identifier']['id'], '22222222')


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(
        set(tender) - set(self.initial_data),
        {
            "id",
            "dateModified",
            "tenderID",
            "date",
            "status",
            "procurementMethod",
            "awardCriteria",
            "submissionMethod",
            "owner",
        },
    )
    self.assertIn(tender["id"], response.headers["Location"])


def get_tender(self):
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
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get("/tenders/{}?opt_pretty=1".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


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
    response = self.app.post_json("/tenders", {"data": data}, status=422)
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
    response = self.app.post_json("/tenders", {"data": data}, status=422)
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
    response = self.app.post_json("/tenders", {"data": data}, status=422)
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
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": [{"value": ["Value should be less than 0.3."]}]}],
                "location": "body",
                "name": "features",
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
                "description": [{"enum": ["Feature value should be uniq for feature"]}],
                "location": "body",
                "name": "features",
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
                "description": ["Feature code should be uniq for all features"],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][1]["code"] = "OCDS-123454-YEARS"
    data["features"][1]["enum"][0]["value"] = 0.2
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Sum of max value of all features for lot should be less then or equal to 30%"],
                "location": "body",
                "name": "features",
            }
        ],
    )


def tender_features(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = "+0440000000"
    item = data["items"][0].copy()
    data["items"] = [item]
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": item["id"],
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": "Років на ринку",
            "title_en": "Years trading",
            "description": "Кількість років, які організація учасник працює на ринку",
            "enum": [{"value": 0.05, "title": "До 3 років"}, {"value": 0.1, "title": "Більше 3 років"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.tender_id = tender["id"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["features"], data["features"])

    # switch to active.enquiries
    self.set_status("active.enquiries")

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


def patch_tender_jsonpatch(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    tender.pop("dateModified")

    import random

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "items": [
                    {
                        "additionalClassifications": [
                            {"scheme": "ДКПП", "id": "{}".format(i), "description": "description #{}".format(i)}
                            for i in random.sample(list(range(30)), 25)
                        ]
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "items": [
                    {
                        "additionalClassifications": [
                            {"scheme": "ДКПП", "id": "{}".format(i), "description": "description #{}".format(i)}
                            for i in random.sample(list(range(30)), 20)
                        ]
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def patch_tender(self):
    data = deepcopy(self.initial_data)
    data["items"].append(deepcopy(data["items"][0]))
    data["items"][-1]["id"] = uuid4().hex
    data["items"][-1]["description"] = "test_description"
    data["procuringEntity"]["contactPoint"]["faxNumber"] = "+0440000000"
    response = self.app.get("/tenders")
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    tender = response.json["data"]
    self.tender_id = tender["id"]
    owner_token = response.json["access"]["token"]

    # switch to active.enquiries
    self.set_status("active.enquiries")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    end_date = calculate_tender_business_date(
        parse_date(tender["tenderPeriod"]["startDate"]), timedelta(days=3), self.tender_class(tender)
    ) - self.get_timedelta(minutes=1)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
        {"data": {"tenderPeriod": {"endDate": end_date.isoformat()}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "tenderPeriod",
            "description": ["tenderPeriod must be at least 3 full calendar days long"]
        }],
    )
    end_date = calculate_tender_business_date(
        parse_date(tender["tenderPeriod"]["startDate"]), timedelta(days=3), tender
    ) + self.get_timedelta(minutes=1)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
        {"data": {"tenderPeriod": {"endDate": end_date.isoformat()}}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotEqual(end_date.isoformat(), tender["tenderPeriod"]["endDate"])

    items = deepcopy(tender["items"])
    items[0]["quantity"] += 1
    items[0]["description"] = "new description"
    items[-1]["quantity"] += 2

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["items"][0]["quantity"], tender["items"][0]["quantity"] + 1)
    self.assertEqual(response.json["data"]["items"][0]["description"], items[0]["description"])
    self.assertEqual(response.json["data"]["items"][1]["quantity"], tender["items"][1]["quantity"] + 2)

    items[0], items[-1] = items[-1], items[0]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": items}}, status=403
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender items. Items order mismatch")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"items": [items[0]]}}, status=403
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender items. Items count mismatch")

    # user cannot patch tender in active.enquiries
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"title": "test_title"}}, status=403)
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))

    # owner can also
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token), {"data": {"title": "test_title"}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["title"], "test_title")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")
    response = self.app.patch_json(
        "/tenders/{}".format(self.tender_id), {"data": {"status": "active.tendering"}}, status=403
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))

    response = self.app.get("/tenders/{}".format(tender["id"]))
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procuringEntity": {"kind": "defense"}}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotEqual(response.json["data"]["procuringEntity"]["kind"], "defense")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": {"contactPoint": {"faxNumber": None}}}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertIn("faxNumber", response.json["data"]["procuringEntity"]["contactPoint"])
    tender = response.json["data"]

    startDate = (parse_date(tender["tenderPeriod"]["startDate"]) + self.get_timedelta(days=1)).isoformat()
    endDate = (parse_date(tender["tenderPeriod"]["endDate"]) + self.get_timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": {"startDate": startDate, "endDate": endDate}}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(endDate, tender["tenderPeriod"]["endDate"])
    self.assertNotEqual(startDate, tender["tenderPeriod"]["startDate"])

    endDate = (parse_date(tender["tenderPeriod"]["endDate"]) + self.get_timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"tenderPeriod": {"endDate": endDate}}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(endDate, tender["tenderPeriod"]["endDate"])

    # we cannot patch tender minimalStep
    new_minimal_step = {"currency": "UAH", "amount": 200.0, "valueAddedTaxIncluded": True}
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"minimalStep": new_minimal_step}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotEqual(response.json["data"]["minimalStep"]["amount"], new_minimal_step["amount"])
    self.assertEqual(response.json["data"]["minimalStep"]["amount"], tender["minimalStep"]["amount"])

    self.set_status("active.tendering")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    # can't startDate either
    startDate = (parse_date(tender["tenderPeriod"]["startDate"]) + self.get_timedelta(days=1)).isoformat()
    endDate = (parse_date(tender["tenderPeriod"]["endDate"]) + self.get_timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": {"startDate": startDate, "endDate": endDate}}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertNotEqual(startDate, tender["tenderPeriod"]["startDate"])

    # can't change endDate either
    endDate = (parse_date(tender["tenderPeriod"]["endDate"]) + self.get_timedelta(days=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"tenderPeriod": {"endDate": endDate}}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertNotEqual(endDate, tender["tenderPeriod"]["endDate"])

    tender_data = self.db.get(tender["id"])
    tender_data["status"] = "complete"
    self.db.save(tender_data)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def patch_items_related_buyer_id(self):
    # create tender with two buyers
    data = deepcopy(self.initial_data)
    test_organization1 = deepcopy(test_organization)
    test_organization2 = deepcopy(test_organization)
    test_organization2["name"] = "Управління міжнародних справ"
    test_organization2["identifier"]["id"] = "00055555"

    data["buyers"] = [
        {"name": test_organization1["name"], "identifier": test_organization1["identifier"]},
        {"name": test_organization2["name"], "identifier": test_organization2["identifier"]},
    ]

    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["buyers"]), 2)

    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    buyer1_id, buyer2_id = response.json["data"]["buyers"][0]["id"], response.json["data"]["buyers"][1]["id"]

    self.assertEqual(len(response.json["data"]["buyers"]), 2)
    self.assertEqual(len(response.json["data"]["items"]), 1)

    self.set_status("active.enquiries")

    patch_request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)

    response = self.app.patch_json(
        patch_request_path,
        {"data": {"items": [{"description_en": "new cases for state awards"}]}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Each item should contain relatedBuyer id',
          'location': 'body',
          'name': 'data'}],
    )
    response = self.app.patch_json(
        patch_request_path,
        {"data": {"items": [
            {
                "description_en": "new cases for state awards",
                "relatedBuyer": buyer1_id
            }
        ]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["description_en"], "new cases for state awards")
    self.assertEqual(response.json["data"]["items"][0]["relatedBuyer"], buyer1_id)


def patch_tender_bot(self):
    # only bot can change tender in draft.pending
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": {"kind": "defense"}}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update tender in current (draft.pending) tender status"
    )

    # tender items are not subset of agreement items
    # TODO: adjust data ti shrink errors only to supposed one
    self.app.authorization = ("Basic", (BOT_NAME, ""))
    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "draft.unsuccessful")
    reasons = set(response.json["data"]["unsuccessfulReason"])
    self.assertFalse(
        reasons.difference(
            set(
                [
                    "agreements[0] status is not active",
                    "agreements[0] items is not subset of tender items",
                    "agreements[0] has less than 3 active contracts",
                ]
            )
        )
    )

    # patch tender with different changes by bot
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement["period"]["endDate"] = (get_now() + timedelta(days=7, minutes=1)).isoformat()
    now = get_now().isoformat()
    agreement["changes"] = [
        {
            "status": "active",
            "modifications": [{"itemId": agreement["items"][0]["id"], "addend": 0.9}],
            "rationaleType": "taxRate",
            "dateSigned": now,
            "rationale": "text taxRate",
            "date": now,
            "id": uuid4().hex,
        },
        {
            "status": "active",
            "modifications": [{"itemId": agreement["items"][0]["id"], "factor": 0.95}],
            "rationaleType": "itemPriceVariation",
            "dateSigned": now,
            "rationale": "text itemPriceVariation",
            "date": now,
            "id": uuid4().hex,
        },
    ]

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.get("/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["changes"], agreement["changes"])

    # patch tender items with correct items by bot
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement["period"]["endDate"] = (get_now() + timedelta(days=7, minutes=1)).isoformat()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")
    self.assertIn("minimalStep", response.json["data"])
    self.assertEqual(
        response.json["data"]["minimalStep"]["amount"], round(response.json["data"]["minimalStep"]["amount"], 2)
    )
    self.assertEqual(
        response.json["data"]["lots"][0]["minimalStep"]["amount"],
        round(response.json["data"]["lots"][0]["minimalStep"]["amount"], 2),
    )
    self.assertEqual(
        calculate_tender_business_date(
            parse_date(response.json["data"]["enquiryPeriod"]["startDate"]),
            ENQUIRY_PERIOD,
            self.tender_class(tender)
        ),
        parse_date(response.json["data"]["enquiryPeriod"]["endDate"]),
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    agreement_contracts = response.json["data"]["agreements"][0]["contracts"]
    max_value = max([contract["value"] for contract in agreement_contracts], key=lambda value: value["amount"])
    self.assertEqual(response.json["data"]["value"], max_value)
    self.assertEqual(response.json["data"]["lots"][0]["value"], max_value)
    # чому цей ассерт не працює не можу роздебажити
    # self.assertNotEqual(response.json['data']['lots'][0]['value'], agreement_contracts[0]['value'])
    self.app.authorization = ("Basic", (BOT_NAME, ""))

    # patch tender by bot in wrong status
    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "draft"}}, status=403)
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update tender in current (active.enquiries) tender status"
    )

    # patch tender agreement more items than tender items, more features then tender features
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    second_item = deepcopy(agreement["items"][0])
    second_item["id"] = uuid4().hex
    agreement["items"] = [agreement["items"][0], second_item]

    features = deepcopy(test_features)
    new_item_feature = deepcopy(features[0])
    new_item_feature["code"] = uuid4().hex
    new_item_feature["relatedItem"] = second_item["id"]

    agreement["features"] = features + [new_item_feature]

    agreement["period"]["endDate"] = (get_now() + timedelta(days=7, minutes=1)).isoformat()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotIn(new_item_feature["code"], (f["code"] for f in tender_data["features"]))
    self.assertIn(second_item["id"], (i["id"] for i in tender_data["agreements"][0]["items"]))

    # patch tender with less than 7 days to end
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    six_days = timedelta(days=6)
    if SANDBOX_MODE:
        six_days = six_days / 1440
    agreement["period"]["endDate"] = (get_now() + six_days).isoformat()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "draft.unsuccessful")
    self.assertEqual(
        response.json["data"]["unsuccessfulReason"],
        ["agreements[0] ends less than {} days".format(MIN_PERIOD_UNTIL_AGREEMENT_END.days)],
    )

    # patch tender argeement.period.startDate > tender.date
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    day = timedelta(days=1)
    if SANDBOX_MODE:
        day = day / 1440
    agreement["period"]["startDate"] = (get_now() + day).isoformat()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "draft.unsuccessful")
    self.assertEqual(response.json["data"]["unsuccessfulReason"], ["agreements[0].period.startDate is > tender.date"])

    # patch tender with less than 3 active contracts
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement["period"]["endDate"] = (get_now() + timedelta(days=7, minutes=1)).isoformat()
    agreement["contracts"] = agreement["contracts"][:2]  # only first and second contract

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "draft.unsuccessful")
    self.assertEqual(
        response.json["data"]["unsuccessfulReason"],
        ["agreements[0] has less than {} active contracts".format(MIN_ACTIVE_CONTRACTS)],
    )

    # patch tender with wrong identifier
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement["procuringEntity"]["identifier"]["id"] = "21725150"  # tender procuringEntity identifier is 00037256

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "draft.unsuccessful")
    self.assertEqual(response.json["data"]["unsuccessfulReason"], [AGREEMENT_IDENTIFIER])

    # patch tender with agreement -> with documents
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement["documents"] = [
        {
            "hash": "md5:639cb23ed3bf9a747cc6b5bfc8221370",
            "format": "text/plain",
            "url": "http://ds.devel.prozorro.office.ovirt/get/21cd6a80c057443393a8a7a02797072e?KeyID=ce4450fc&Signature=r6quaDNKEjMscqPQJN%2FkHv%2F9sHYpGj9xDDgSLn56BTmCe8NB9P3pxALWHqyP%252BTDtFzsJFlWK%252Bid891AocS0jDA%253D%253D",
            "title": "d-86e3290dsimilique1RbUsG.docx",
            "documentOf": "agreement",
            "datePublished": "2018-10-16T15:12:43.465552+03:00",
            "dateModified": "2018-10-16T15:12:43.465573+03:00",
            "id": "4894210d5a3e4dc29bfd11ec3e2db913",
        }
    ]

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    response = self.app.get("/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertNotIn("documents", response.json["data"])

    # test tenderPeriod.endDate
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    tender_period_start_date = calculate_tender_business_date(get_now(), -TENDERING_DURATION)
    tender_doc = self.db.get(self.tender_id)
    tender_doc["enquiryPeriod"]["startDate"] = tender_period_start_date.isoformat()
    tender_doc["enquiryPeriod"]["endDate"] = tender_period_start_date.isoformat()
    tender_doc["tenderPeriod"]["startDate"] = tender_period_start_date.isoformat()
    tender_doc["tenderPeriod"]["endDate"] = get_now().isoformat()
    self.db.save(tender_doc)

    self.app.authorization = ("Basic", (BOT_NAME, ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


@mock.patch("openprocurement.tender.core.models.CANT_DELETE_PERIOD_START_DATE_FROM", get_now() - timedelta(days=1))
def required_field_deletion(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    # TODO: Test all the required fields
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"enquiryPeriod": {"startDate": None}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"startDate": ["This field cannot be deleted"]},
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"tenderPeriod": {"startDate": None}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"startDate": ["This field cannot be deleted"]},
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )


def dateModified_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual((response.status, response.content_type), ("201 Created", "application/json"))
    tender = response.json["data"]
    self.tender_id = tender["id"]
    token = response.json["access"]["token"]
    dateModified = tender["dateModified"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def tender_not_found(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/tenders/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.patch_json("/tenders/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    # put custom document object into database to check tender construction on non-Tender data
    data = {"contract": "test", "_id": uuid4().hex}
    self.db.save(data)

    response = self.app.get("/tenders/{}".format(data["_id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")


def guarantee(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("guarantee", response.json["data"])
    tender = response.json["data"]
    self.tender_id = tender["id"]
    token = response.json["access"]["token"]

    # switch to active.enquiries
    self.set_status("active.enquiries")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"guarantee": {"amount": 55}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 55)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"guarantee": {"currency": "USD"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"amount": 100500, "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"guarantee": None}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    data = deepcopy(self.initial_data)
    data["guarantee"] = {"amount": 100, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {"description": {"valueAddedTaxIncluded": "Rogue field"}, "location": "body", "name": "guarantee"},
    )


def tender_Administrator_change(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    # response = self.app.post_json('/tenders/{}/questions'.format(tender['id']), {'data': {'title': 'question title', 'description': 'question description', 'author': test_author}})
    # self.assertEqual(response.status, '201 Created')
    # self.assertEqual(response.content_type, 'application/json')
    # question = response.json['data']

    authorization = self.app.authorization
    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}".format(tender["id"]),
        {"data": {"mode": "test", "procuringEntity": {"identifier": {"id": "00000000"}}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], "test")
    self.assertEqual(response.json["data"]["procuringEntity"]["identifier"]["id"], "00000000")

    # response = self.app.patch_json('/tenders/{}/questions/{}'.format(tender['id'], question['id']), {"data": {"answer": "answer"}}, status=403)
    # self.assertEqual(response.status, '403 Forbidden')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['errors'], [
    # {"location": "url", "name": "role", "description": "Forbidden"}
    # ])
    self.app.authorization = authorization

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender["id"], token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"mode": "test"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], "test")


def patch_not_author(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "draft.pending"}}
    )

    authorization = self.app.authorization
    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post(
        "/tenders/{}/documents".format(tender["id"]), upload_files=[("file", "name.doc", b"content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.app.authorization = authorization
    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(tender["id"], doc_id, owner_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")


# TenderProcessTest


def invalid_tender_conditions(self):
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

    response = self.app.post_json(
        "/tenders/{}/complaints".format(tender_id),
        {
            "data": test_claim
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "text/plain")

    # cancellation
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
        activate_cancellation_without_complaints_after_2020_04_19(
            self,
            cancellation_id,
            tender_id,
            owner_token
        )
    # check status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_valid_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    response = self.set_status(
        "active.tendering", {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}]}
    )
    self.assertIn("auctionPeriod", response.json["data"]["lots"][0])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "tenderers": [test_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_data["lots"][0]["id"]}],
            }
        },
    )
    # switch to active.qualification
    self.set_status("active.tendering", start_end="end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    award_date = [i["date"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    self.assertNotEqual(response.json["data"]["date"], award_date)

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("active.awarded", start_end="end")
    # time travel
    tender = self.db.get(tender_id)
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


def one_invalid_bid_tender(self):
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
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "tenderers": [test_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_data["lots"][0]["id"]}],
            }
        },
    )
    # switch to active.qualification
    self.set_status("active.tendering", start_end="end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update award status to unsuccessful, if tender status is active.qualification"
        " and there is no cancelled award with the same bid_id",
    )

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, owner_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    new_award_id = response.json["data"]["awards"][-1]["id"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, new_award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))

    response = self.app.get("/tenders/{}".format(tender_id))
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
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "tenderers": [test_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_data["lots"][0]["id"]}],
            }
        },
    )
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "tenderers": [test_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_data["lots"][0]["id"]}],
            }
        },
    )
    # switch to active.auction
    self.set_status("active.auction")

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertIn("agreements", response.json["data"])

    lot_id = self.initial_data["lots"][0]["id"]
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "lots": [{"auctionUrl": "https://tender.auction.url"}],
                "bids": [
                    {
                        "id": i["id"],
                        "lotValues": [
                            {
                                "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"]),
                                "relatedLot": lot_id,
                            }
                        ],
                    }
                    for i in auction_bids_data
                ],
            }
        },
    )
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id), {"data": {"bids": auction_bids_data}}
    )

    ## get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]
    # create tender contract document for test
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender_id, contract_id, owner_token),
        upload_files=[("file", "name.doc", b"content")],
        status=201,
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("active.awarded", start_end="end")

    tender = self.db.get(tender_id)
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
        upload_files=[("file", "name.doc", b"content")],
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
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def lost_contract_for_active_award(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "tenderers": [test_organization],
                "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_data["lots"][0]["id"]}],
            }
        },
    )
    # switch to active.qualification
    self.set_status("active.tendering", start_end="end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
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


def patch_tender_to_draft_pending(self):
    data = self.initial_data.copy()
    data.pop("agreements")
    data.update({"status": "active.tendering"})
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status_code, 422)
    self.assertEqual(response.json["errors"][0]["description"][0], "Please provide at least 1 item.")


def edit_tender_in_active_enquiries(self):
    tender, owner_token = self.create_tender_and_prepare_for_bot_patch()
    agreement = deepcopy(self.initial_agreement)
    agreement["period"]["endDate"] = (get_now() + timedelta(days=7, minutes=1)).isoformat()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id), {"data": agreement}
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["agreementID"], self.initial_agreement["agreementID"])

    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"status": "active.enquiries"}})
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")
    self.assertIn("minimalStep", response.json["data"])
    self.assertEqual(
        response.json["data"]["minimalStep"]["amount"], round(response.json["data"]["minimalStep"]["amount"], 2)
    )
    self.assertEqual(
        response.json["data"]["lots"][0]["minimalStep"]["amount"],
        round(response.json["data"]["lots"][0]["minimalStep"]["amount"], 2),
    )
    self.assertEqual(
        calculate_tender_business_date(
            parse_date(response.json["data"]["enquiryPeriod"]["startDate"]),
            ENQUIRY_PERIOD,
            self.tender_class(tender)
        ),
        parse_date(response.json["data"]["enquiryPeriod"]["endDate"]),
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender_data = response.json["data"]
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")

    allowed_modify = (
        "title",
        "guarantee",
        "lots[0].title",
        "lots[0].description",
        "items[0].description",
        "items[0].deliveryAddress",
        "items[0].deliveryDate",
        "tenderPeriod.endDate",
    )
    denied_modify = (
        "status",
        "lots[0].status",
        "items[0].unit",
        "items[0].classification",
        "items[0].additionalClassifications[0]",
        "tenderPeriod.startDate",
        "procuringEntity",
    )

    data = {
        "title": "Tender title active.enquiries.",
        "status": "active.auction",
        "guarantee": {"amount": 100500, "currency": "UAH"},
        "lots": [
            {
                "title": "Lot title active.enquiries.",
                "description": "Lot description active.enquiries.",
                "status": "unsuccessful",
            }
        ],
        "items": [
            {
                "description": "Item description active.enquiries.",
                "quantity": 123,
                "classification": {
                    "scheme": "ДК021",
                    "id": "45112000-5",
                    "description": "Active.Enquiries CPV Description.",
                    "description_en": "EN active.enquiries CPV description.",
                },
                "additionalClassifications": [
                    {
                        "scheme": "ДК021",
                        "id": "4409000-9",
                        "description": "Active.Enquiries additioanlClassfications description.",
                    }
                ],

                "deliveryAddress": {
                    "countryName": "Україна",
                    "postalCode": "46010",
                    "region": "Тернопільська область",
                    "streetAddress": "Текстильная вул. 14",
                    "locality": "м. Тернопіль",
                },

                "deliveryDate": {
                    "startDate": get_now().isoformat(),
                    "endDate": (get_now() + timedelta(days=92)).isoformat(),
                },
                "unit": {"code": "LTR", "name": "Sheet"},
            }
        ],

        "procuringEntity": {
            "name": "Державне управління справами1",
            "kind": "other",
            "identifier": {"scheme": "UA-EDR", "id": "0000000", "uri": "http://www.dus1.gov.ua/"},
            "address": {
                "countryName": "Україна",
                "postalCode": "01220",
                "region": "м. Київ",
                "locality": "м. Київ",
                "streetAddress": "вул. Банкова, 11, корпус 11",

            },
            "contactPoint": {
                "name": "Державне управління справами 1",
                "telephone": "+0440000001",
                "availableLanguage": "uk",
            },
            "additionalContactPoints": [
                {"name": "Державне управління справами 2", "telephone": "+044000001", "availableLanguage": "en"}
            ],
        },
        "tenderPeriod": {
            "startDate": (get_now() + timedelta(days=10)).isoformat(),
            "endDate": (get_now() + timedelta(days=33)).isoformat(),
        },
    }

    # Make sure that new data not equal to current tender data
    for path in allowed_modify + denied_modify:
        self.assertNotEqual(jmespath.search(path, response.json["data"]), jmespath.search(path, data))

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": data})
    patched_tender = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    for path in allowed_modify:
        self.assertEqual(jmespath.search(path, data), jmespath.search(path, patched_tender))
    for path in denied_modify:
        self.assertNotEqual(jmespath.search(path, data), jmespath.search(path, patched_tender))
        self.assertEqual(jmespath.search(path, tender_data), jmespath.search(path, patched_tender))

    response = self.app.get("/tenders/{}".format(tender["id"]))
    patched_tender = response.json["data"]
    for path in allowed_modify:
        self.assertEqual(jmespath.search(path, data), jmespath.search(path, patched_tender))
    for path in denied_modify:
        self.assertNotEqual(jmespath.search(path, data), jmespath.search(path, patched_tender))
        self.assertEqual(jmespath.search(path, tender_data), jmespath.search(path, patched_tender))
