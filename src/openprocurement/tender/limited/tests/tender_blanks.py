# -*- coding: utf-8 -*-
from copy import deepcopy

import mock
from datetime import timedelta

from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    ROUTE_PREFIX,
    CPV_ITEMS_CLASS_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    RELEASE_2020_04_19,
)
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_cancellation
from openprocurement.tender.core.tests.cancellation import activate_cancellation_after_2020_04_19

from openprocurement.tender.limited.models import NegotiationTender, NegotiationQuickTender, ReportingTender


def create_tender_accreditation(self):
    for broker in ["broker1", "broker3"]:
        self.app.authorization = ("Basic", (broker, ""))
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    for broker in ["broker2", "broker4"]:
        self.app.authorization = ("Basic", (broker, ""))
        response = self.app.post_json("/tenders", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Broker Accreditation level does not permit tender creation"
        )

    self.app.authorization = ("Basic", ("broker1t", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Broker Accreditation level does not permit tender creation"
    )


def simple_add_tender(self):
    u = ReportingTender(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "reporting"
    assert u.procurementMethodType == fromdb["procurementMethodType"]

    u.delete_instance(self.db)


def simple_add_tender_negotiation(self):
    u = NegotiationTender(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "negotiation"
    assert u.procurementMethodType == fromdb["procurementMethodType"]

    u.delete_instance(self.db)


def simple_add_tender_negotiation_quick(self):
    u = NegotiationQuickTender(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "negotiation.quick"
    assert u.procurementMethodType == fromdb["procurementMethodType"]

    u.delete_instance(self.db)


def listing(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tenders.append(response.json["data"])

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

    response = self.app.get("/tenders", params=[("opt_fields", "status")])
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

    test_tender_data2 = self.initial_data.copy()
    test_tender_data2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/tenders?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def tender_award_create(self):
    data = self.initial_data.copy()
    award_id = "1234" * 8
    data["awards"] = [
        {
            "suppliers": [test_organization],
            "subcontractingDetails": "Details",
            "status": "pending",
            "qualified": True,
            "id": award_id,
        }
    ]

    data["contracts"] = [{"title": "contract title", "description": "contract description", "awardID": award_id}]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("contracts", response.json["data"])
    self.assertNotIn("awards", response.json["data"])


def listing_changes(self):
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tenders.append(response.json["data"])

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

    test_tender_data2 = self.initial_data.copy()
    test_tender_data2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/tenders?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


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

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "reporting", "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "reporting", "value": "invalid_value"}}, status=422
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
        request_path, {"data": {"procurementMethodType": "reporting", "procurementMethod": "invalid_value"}}, status=422
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
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"value"}, response.json["errors"]
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


def field_relatedLot(self):
    request_path = "/tenders"
    data = deepcopy(self.initial_data)
    data["items"][0]["relatedLot"] = uuid4().hex
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"relatedLot": [u"This option is not available"]}],
                u"location": u"body",
                u"name": u"items",
            }
        ],
    )


def create_tender_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash", "doc_id": "hash2", "tenderID": "hash3"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    fields = [
        u"id",
        u"dateModified",
        u"tenderID",
        u"status",
        u"items",
        u"value",
        u"procuringEntity",
        u"owner",
        u"procurementMethod",
        u"procurementMethodType",
        u"title",
        u"date",
        u"mainProcurementCategory",
        u"milestones",
    ]
    if u"procurementMethodDetails" in self.initial_data:
        fields.append(u"procurementMethodDetails")
    if "negotiation" == self.initial_data["procurementMethodType"]:
        fields.append(u"cause")
    if "negotiation.quick" == self.initial_data["procurementMethodType"]:
        fields.append(u"cause")
    if "negotiation" in self.initial_data["procurementMethodType"]:
        fields.append(u"causeDescription")
    self.assertEqual(set(tender), set(fields))
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])


def create_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"value": {"amount": 100}}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Can't update tender in current (draft) status", u"location": u"body", u"name": u"data"}],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active")


def create_tender(self):
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
    if "negotiation" == self.initial_data["procurementMethodType"]:
        tender_set.remove(u"cause")
    if "negotiation" in self.initial_data["procurementMethodType"]:
        tender_set.remove(u"causeDescription")
    self.assertEqual(
        tender_set - set(self.initial_data),
        set([u"id", u"date", u"dateModified", u"owner", u"tenderID", u"status", u"procurementMethod"]),
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

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryAddress"]["postalCode"]
    del data["items"][0]["deliveryAddress"]["locality"]
    del data["items"][0]["deliveryAddress"]["streetAddress"]
    del data["items"][0]["deliveryAddress"]["region"]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("postalCode", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("locality", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("streetAddress", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("region", response.json["data"]["items"][0]["deliveryAddress"])

    initial_data = deepcopy(self.initial_data)
    initial_data["items"][0]["classification"]["id"] = "99999999-9"
    additional_classification = initial_data["items"][0].pop("additionalClassifications")
    additional_classification[0]["scheme"] = "specialNorms"
    if get_now() > NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM:
        response = self.app.post_json("/tenders", {"data": initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
        self.assertEqual(tender["items"][0]["classification"]["id"], "99999999-9")
        self.assertNotIn("additionalClassifications", tender["items"][0])

    initial_data["items"][0]["additionalClassifications"] = additional_classification
    response = self.app.post_json("/tenders", {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["items"][0]["classification"]["id"], "99999999-9")
    self.assertEqual(tender["items"][0]["additionalClassifications"], additional_classification)


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procurementMethodRationale": "Limited"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    new_dateModified = new_tender.pop("dateModified")
    tender["procurementMethodRationale"] = "Limited"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"dateModified": new_dateModified}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender2 = response.json["data"]
    new_dateModified2 = new_tender2.pop("dateModified")
    self.assertEqual(new_tender, new_tender2)
    self.assertEqual(new_dateModified, new_dateModified2)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procuringEntity": {"kind": "defense"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["procuringEntity"]["kind"], "defense")

    revisions = self.db.get(tender["id"]).get("revisions")
    self.assertEqual(revisions[-1][u"changes"][0]["op"], u"remove")
    self.assertEqual(revisions[-1][u"changes"][0]["path"], u"/procurementMethodRationale")

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
                            "scheme": "ДК021",
                            "id": "55523100-3",
                            "description": "Послуги з харчування у школах",
                        }
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
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

    # The following operations are performed for a proper transition to the "Complete" tender status

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender["id"], owner_token),
        {"data": {"suppliers": [test_organization], "status": "pending"}},
    )
    award_id = response.json["data"]["id"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender["id"], award_id, owner_token),
        {"data": {"qualified": True, "status": "active"}},
    )

    response = self.app.get("/tenders/{}/contracts".format(tender["id"]))
    contract_id = response.json["data"][0]["id"]

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender["id"], contract_id, owner_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")

    save_tender = self.db.get(tender["id"])
    for i in save_tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # works for negotiation tender
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(save_tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender["id"], contract_id, owner_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def tender_Administrator_change(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    authorization = self.app.authorization
    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}".format(tender["id"]),
        {"data": {"mode": u"test", "procuringEntity": {"identifier": {"id": "00000000"}}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], u"test")
    self.assertEqual(response.json["data"]["procuringEntity"]["identifier"]["id"], "00000000")

    self.app.authorization = authorization

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json("/tenders/{}".format(tender["id"]), {"data": {"mode": u"test"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], u"test")


def field_relatedLot_negotiation(self):
    request_path = "/tenders"
    data = deepcopy(self.initial_data)
    data["items"][0]["relatedLot"] = uuid4().hex
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"relatedLot": [u"relatedLot should be one of lots"]}],
                u"location": u"body",
                u"name": u"items",
            }
        ],
    )


def changing_tender_after_award(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    first_lot = response.json["data"]

    # create second lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # change tender
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"description": "New description"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "New description")

    # first award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "status": "pending", "lotID": first_lot["id"], "qualified": True}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # change tender
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"description": "New description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender when there is at least one award.")


def initial_lot_date(self):
    # create tender were initial data has lots
    lots = deepcopy(self.test_lots_data) * 2
    data = deepcopy(self.initial_data)
    data["lots"] = lots
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # check if initial lots have date
    response = self.app.get("/tenders/{}".format(tender_id))
    lots = response.json["data"]["lots"]
    self.assertIn("date", lots[0])
    self.assertIn("date", lots[1])

    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # check all lots has a initial date
    response = self.app.get("/tenders/{}".format(tender_id))
    lots = response.json["data"]["lots"]
    self.assertIn("date", lots[0])
    self.assertIn("date", lots[1])
    self.assertIn("date", lots[2])


def tender_status_change(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"status": "complete"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Chronograph has no power over me!")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"status": "complete"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active")

    # try to mark tender complete
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"status": "complete"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def tender_negotiation_status_change(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"status": "complete"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active")

    # try to mark tender complete
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"status": "complete"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def single_award_tender(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.json["data"], [])

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards".format(tender_id),
        {"data": {"suppliers": [test_organization], "value": {"amount": 500}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))

    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"qualified": True, "status": "active"}},
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # sign contract
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    # create new tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)

    # get last award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    self.assertEqual(contract["awardID"], award_id)

    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # set award to cancelled
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # try to sign contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract["id"], owner_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update contract in current (cancelled) status")

    # tender status remains the same
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active")


def multiple_awards_tender(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.json["data"], [])

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards".format(tender_id),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 500}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    award = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token),
        {"data": {"qualified": True, "status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 501}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't create new award while any (active) award exists"
    )

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token),
        {"data": {"status": "cancelled"}},
    )

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 505}}},
    )
    self.assertEqual(response.status, "201 Created")

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 2)

    # get last award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    self.assertEqual(contract["awardID"], award_id)

    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # sign contract
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract["id"], owner_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_cancellation(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token =  response.json["access"]["token"]

    # create cancellation
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cacnellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cacnellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "cancelled")

    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")

    # create cancellation
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(
            self,
            cancellation_id,
            tender_id,
            owner_token
        )
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "cancelled")

    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)
    award = response.json["data"][0]
    self.assertEqual(award["status"], "pending")

    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    self.set_all_awards_complaint_period_end()

    # create cancellation in stand still
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(
            self,
            cancellation_id,
            tender_id,
            owner_token
        )

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "cancelled")

    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)
    award = response.json["data"][0]
    self.assertEqual(award["status"], "pending")

    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # works for negotiation tender
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": {"valueAddedTaxIncluded": False}}},
    )
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")

    self.set_all_awards_complaint_period_end()

    # create cancellation
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")


def tender_cause(self):
    data = deepcopy(self.initial_data)

    del data["cause"]
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"cause"}],
    )

    data["cause"] = "noCompetition"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")

    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"cause": "artContestIP"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["cause"], "artContestIP")


def tender_cause_quick(self):
    data = deepcopy(self.initial_data)
    del data["cause"]

    constant_target = "openprocurement.tender.limited.models.QUICK_CAUSE_REQUIRED_FROM"

    with mock.patch(constant_target, get_now() + timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data})

    self.assertEqual(response.status, "201 Created")

    with mock.patch(constant_target, get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"cause"}],
    )

    data["cause"] = "quick"

    with mock.patch(constant_target, get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data})

    self.assertEqual(response.status, "201 Created")


def tender_cause_choices(self):
    data = deepcopy(self.initial_data)

    data["cause"] = "unexisting value"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    cause_choices = [
        "artContestIP",
        "noCompetition",
        "twiceUnsuccessful",
        "additionalPurchase",
        "additionalConstruction",
        "stateLegalServices",
    ]
    if "negotiation.quick" == data["procurementMethodType"]:
        cause_choices = ['quick'] + cause_choices

    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Value must be one of ['{}'].".format("', '".join(cause_choices))],
                u"location": u"body",
                u"name": u"cause",
            }
        ],
    )


def tender_cause_desc(self):
    data = deepcopy(self.initial_data)
    del data["causeDescription"]
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"causeDescription"}],
    )

    data["causeDescription"] = ""
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"String value is too short."], u"location": u"body", u"name": u"causeDescription"}],
    )

    data["causeDescription"] = "blue pine"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["causeDescription"], "blue pine")


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
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "goods")

    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update tender in active status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "services"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")
