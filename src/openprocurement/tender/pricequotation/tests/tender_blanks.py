# -*- coding: utf-8 -*-
import mock
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    ROUTE_PREFIX,
    CPV_BLOCK_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    SANDBOX_MODE,
    CPV_ITEMS_CLASS_FROM,
)
from openprocurement.tender.pricequotation.models import PriceQuotationTender as Tender
from openprocurement.tender.pricequotation.tests.base import (
    test_organization,
    test_cancellation,
    test_shortlisted_firms,
    test_short_profile,
    test_requirement_response_valid,
)
from openprocurement.tender.pricequotation.tests.data import test_milestones
# TenderTest
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.pricequotation.constants import PMT, PQ_KINDS


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
        self.tender_id = response.json['data']['id']
        self.set_status('active.tendering')
        tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
        tenders.append(tender)

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


def listing_changes(self):
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.tender_id = response.json['data']['id']
        self.set_status('active.tendering')
        tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
        tenders.append(tender)
    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(response.status, "200 OK")
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

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status")])
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


def listing_draft(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.tender_id = response.json['data']['id']
        self.set_status('active.tendering')
        tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
        tenders.append(tender)

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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value", "procurementMethodType": PMT}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"value": "invalid_value", "procurementMethodType": PMT}}, status=422)
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

    response = self.app.post_json(request_path, {"data": {"procurementMethod": "invalid_value", "procurementMethodType": PMT }}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertIn(
        {
            u"description": [u"Value must be one of ['selective']."],
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
                    u"description": [{u"additionalClassifications": [u"This field is required."]}],
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

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = u"160173000-1"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(u"classification", response.json["errors"][0][u"description"][0])
    self.assertIn(u"id", response.json["errors"][0][u"description"][0][u"classification"])
    self.assertIn("Value must be one of [u", response.json["errors"][0][u"description"][0][u"classification"][u"id"][0])

    cpv = self.initial_data["items"][0]["classification"]["id"]
    if get_now() < CPV_BLOCK_FROM:
        self.initial_data["items"][0]["classification"]["scheme"] = u"CPV"
    self.initial_data["items"][0]["classification"]["id"] = u"00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    if get_now() < CPV_BLOCK_FROM:
        self.initial_data["items"][0]["classification"]["scheme"] = u"CPV"
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(u"classification", response.json["errors"][0][u"description"][0])
    self.assertIn(u"id", response.json["errors"][0][u"description"][0][u"classification"])
    self.assertIn("Value must be one of [u", response.json["errors"][0][u"description"][0][u"classification"][u"id"][0])

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
                u"description": u"'' procuringEntity cannot publish this type of procedure. "
                u"Only general, special, defense, other, social, authority are allowed.",
                u"location": u"procuringEntity",
                u"name": u"kind",
            }
        ],
    )

    data = deepcopy(self.initial_data)
    data['milestones'] = test_milestones
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{
            u"description": [u"Milestones are not applicable to pricequotation"],
            u"location": u"body",
            u"name": u"milestones"
        }],
    )

    data = deepcopy(self.initial_data)
    data["procuringEntity"]['kind'] = 'central'
    response = self.app.post_json(request_path, {"data": data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{
            u"description": "u'central' procuringEntity cannot publish this type of procedure. Only general, special, defense, other, social, authority are allowed.",
            u"location": u"procuringEntity",
            u"name": u"kind"
        }],
    )


def create_tender_with_inn(self):
    request_path = "/tenders"

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = u"33611000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.assertEqual(response.status, "201 Created")

    addit_classif = [
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = u"33652000-5"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.assertEqual(response.status, "201 Created")


def create_tender_generated(self):
    data = self.initial_data.copy()
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
                u"date",
                u"dateModified",
                u"tenderID",
                u"status",
                u"tenderPeriod",
                u"items",
                u"procuringEntity",
                u"procurementMethod",
                u"awardCriteria",
                u"submissionMethod",
                u"title",
                u"owner",
                u"mainProcurementCategory",
                u"profile",
                u"value"
            ]
        ),
    )
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
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")
    self.assertNotIn("noticePublicationDate", tender)
    self.assertNotIn("unsuccessfulReason", tender)

    if SANDBOX_MODE:
        period = {
            'endDate': (get_now() + timedelta(minutes=1)).isoformat()
        }
    else:
        period = {
            'endDate': (get_now() + timedelta(days=1)).isoformat()
        }

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"status": self.primary_tender_status, "tenderPeriod": period}},
        status=422
    )

    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'tenderPeriod must be at least 2 full business days long'],
          u'location': u'body',
          u'name': u'tenderPeriod'}]
    )

    forbidden_statuses = ("draft.unsuccessful", "active.tendering", "active.qualification", "active.awarded",
                          "complete", "cancelled", "unsuccessful")
    current_status = tender["status"]
    for forbidden_status in forbidden_statuses:
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], token),
            {"data": {"status": forbidden_status}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json['status'], "error")
        self.assertEqual(
            response.json['errors'],
            [{u'description': u"tender_owner can't switch tender from status ({}) to ({})".format(current_status,
                                                                                                  forbidden_status),
              u'location': u'body',
              u'name': u'data'}]
        )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"procuringEntity": {"kind": 'central'}}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{
            u'description': u"u'central' procuringEntity cannot publish this type of procedure. Only general, special, defense, other, social, authority are allowed.",
            u'location': u'procuringEntity',
            u'name': u'kind'
        }]
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"status": self.primary_tender_status, "unsuccessfulReason": ["some value from buyer"]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)
    self.assertEqual(tender["noticePublicationDate"], tender["tenderPeriod"]["startDate"])
    self.assertNotIn("unsuccessfulReason", tender)

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)


def create_tender_in_not_draft_status(self):
    data = self.initial_data.copy()
    forbidden_statuses = ("draft.unsuccessful", "active.tendering", "active.qualification", "active.awarded",
                          "complete", "cancelled", "unsuccessful")
    for forbidden_status in forbidden_statuses:
        data.update({"status": forbidden_status})
        response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
        token = response.json["access"]["token"]
        self.assertEqual(tender["status"], "draft")


def tender_owner_can_change_in_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    general = {
        "numberOfBidders": 1,
        "tenderPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
        "procuringEntity": {"name": u"Національне управління справами"},
        "mainProcurementCategory": u"services",
        "guarantee": {"amount": 50},
    }
    descriptions = {
        "description": u"Some text 1",
        "description_en": u"Some text 2",
        "description_ru": u"Some text 3",
        "procurementMethodRationale": u"Some text 4",
        "procurementMethodRationale_en": u"Some text 5",
        "procurementMethodRationale_ru": u"Some text 6",
        "submissionMethodDetails": u"Some text 7",
        "submissionMethodDetails_en": u"Some text 8",
        "submissionMethodDetails_ru": u"Some text 9"
    }
    titles = {
        "title": u"Test title 1",
        "title_en": u"Test title 2",
        "title_ru": u"Test title 3"
    }
    criterias = {
        "eligibilityCriteria": u"Test criteria 1",
        "eligibilityCriteria_en": u"Test criteria 2",
        "eligibilityCriteria_ru": u"Test criteria 3",
        "awardCriteriaDetails": u"Test criteria 4",
        "awardCriteriaDetails_en": u"Test criteria 5",
        "awardCriteriaDetails_ru": u"Test criteria 6"
    }
    lists = {
        "buyers": [
            {
                "name": u"John Doe",
                "identifier": {
                    "scheme": u"AE-DCCI",
                    "id": u"AE1"
                }
            }
        ],
        "funders": [
            {
                "name": u"First funder",
                "identifier": {
                    "scheme": u"XM-DAC",
                    "id": u"44000"
                },
                "address": {
                    "countryName": u"Японія"
                },
                "contactPoint": {
                    "name": u"Funder name",
                    "email": u"fake_japan_email@gmail.net"
                }
            }
        ],
        "items": [
            {
                "description": u"New description"
            }
        ]
    }
    status = {
        "status": "draft.publishing"
    }

    # general
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": general}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["numberOfBidders"], general["numberOfBidders"])
    self.assertNotEqual(tender["numberOfBidders"], data.get("numberOfBidders"))
    self.assertEqual(tender["mainProcurementCategory"], general["mainProcurementCategory"])
    self.assertNotEqual(tender["mainProcurementCategory"], data.get("mainProcurementCategory"))
    self.assertEqual(tender["tenderPeriod"]["endDate"], general["tenderPeriod"]["endDate"])
    self.assertNotEqual(tender["tenderPeriod"]["endDate"], data.get("tenderPeriod", {}).get("endDate"))
    self.assertEqual(tender["procuringEntity"]["name"], general["procuringEntity"]["name"])
    self.assertNotEqual(tender["procuringEntity"]["name"], data.get("procuringEntity", {}).get("name"))
    self.assertEqual(tender["guarantee"]["amount"], general["guarantee"]["amount"])
    self.assertNotEqual(tender["guarantee"]["amount"], data.get("guarantee", {}).get("amount"))

    # descriptions
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": descriptions}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["description"], descriptions["description"])
    self.assertNotEqual(tender["description"], data.get("description"))
    self.assertEqual(tender["description_en"], descriptions["description_en"])
    self.assertNotEqual(tender["description_en"], data.get("description_en"))
    self.assertEqual(tender["description_ru"], descriptions["description_ru"])
    self.assertNotEqual(tender["description_ru"], data.get("description_ru"))
    self.assertEqual(tender["procurementMethodRationale"], descriptions["procurementMethodRationale"])
    self.assertNotEqual(tender["procurementMethodRationale"], data.get("procurementMethodRationale"))
    self.assertEqual(tender["procurementMethodRationale_en"], descriptions["procurementMethodRationale_en"])
    self.assertNotEqual(tender["procurementMethodRationale_en"], data.get("procurementMethodRationale_en"))
    self.assertEqual(tender["procurementMethodRationale_ru"], descriptions["procurementMethodRationale_ru"])
    self.assertNotEqual(tender["procurementMethodRationale_ru"], data.get("procurementMethodRationale_ru"))
    self.assertEqual(tender["submissionMethodDetails"], descriptions["submissionMethodDetails"])
    self.assertNotEqual(tender["submissionMethodDetails"], data.get("submissionMethodDetails"))
    self.assertEqual(tender["submissionMethodDetails_en"], descriptions["submissionMethodDetails_en"])
    self.assertNotEqual(tender["submissionMethodDetails_en"], data.get("submissionMethodDetails_en"))
    self.assertEqual(tender["submissionMethodDetails_ru"], descriptions["submissionMethodDetails_ru"])
    self.assertNotEqual(tender["submissionMethodDetails_ru"], data.get("submissionMethodDetails_ru"))

    # titles
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": titles}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["title"], titles["title"])
    self.assertNotEqual(tender["title"], data.get("title"))
    self.assertEqual(tender["title_en"], titles["title_en"])
    self.assertNotEqual(tender["title_en"], data.get("title_en"))
    self.assertEqual(tender["title_ru"], titles["title_ru"])
    self.assertNotEqual(tender["title_ru"], data.get("title_ru"))

    # criterias
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": criterias}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["eligibilityCriteria"], criterias["eligibilityCriteria"])
    self.assertNotEqual(tender["eligibilityCriteria"], data.get("eligibilityCriteria"))
    self.assertEqual(tender["eligibilityCriteria_en"], criterias["eligibilityCriteria_en"])
    self.assertNotEqual(tender["eligibilityCriteria_en"], data.get("eligibilityCriteria_en"))
    self.assertEqual(tender["eligibilityCriteria_ru"], criterias["eligibilityCriteria_ru"])
    self.assertNotEqual(tender["eligibilityCriteria_ru"], data.get("eligibilityCriteria_ru"))
    self.assertEqual(tender["awardCriteriaDetails"], criterias["awardCriteriaDetails"])
    self.assertNotEqual(tender["awardCriteriaDetails"], data.get("awardCriteriaDetails"))
    self.assertEqual(tender["awardCriteriaDetails_en"], criterias["awardCriteriaDetails_en"])
    self.assertNotEqual(tender["awardCriteriaDetails_en"], data.get("awardCriteriaDetails_en"))
    self.assertEqual(tender["awardCriteriaDetails_ru"], criterias["awardCriteriaDetails_ru"])
    self.assertNotEqual(tender["awardCriteriaDetails_ru"], data.get("awardCriteriaDetails_ru"))

    # lists
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": lists}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["funders"], lists["funders"])
    self.assertEqual(tender["buyers"], lists["buyers"])

    self.assertEqual(tender["items"][0]["description"], lists["items"][0]["description"])

    # status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": status}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["status"], status["status"])
    self.assertNotEqual(tender["status"], data["status"])


def tender_owner_cannot_change_in_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    general = {
        "tenderID": u"Some id",
        "procurementMethodType": u"belowThreshold",
        "procurementMethod": u"selective",
        "submissionMethod": u"written",
        "awardCriteria": u"bestProposal",
        "mode": u"test"
    }
    owner = {
        "owner": u"Test owner",
        "transfer_token": u"17bc682ec79245bca7d9cdbabbfce8f8",
        "owner_token": u"17bc682ec79245bca7d9cdbabbfce8f7"
    }
    time = {
        "awardPeriod": {"endDate": (get_now() + timedelta(days=14)).isoformat()},
        "date": (get_now() + timedelta(days=1)).isoformat(),
        "dateModified": (get_now() + timedelta(days=1)).isoformat(),
    }
    lists = {
        "revisions": [{"author": "Some author"}],
        "plans": [{"id": uuid4().hex}],
        "cancellations": [
            {
                "reason": u"Some reason",
                "reasonType": u"noDemand"
            }
        ],
    }

    # general
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": general}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertNotEqual(tender.get("tenderID"), general["tenderID"])
    self.assertNotEqual(tender.get("procurementMethodType"), general["procurementMethodType"])
    self.assertEqual(tender.get("procurementMethod"), general["procurementMethod"])
    self.assertNotEqual(tender.get("submissionMethod"), general["submissionMethod"])
    self.assertNotEqual(tender.get("awardCriteria"), general["awardCriteria"])
    self.assertNotEqual(tender.get("mode"), general["mode"])

    # owner
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": owner}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertNotEqual(tender.get("owner"), owner["owner"])
    self.assertNotEqual(tender.get("transfer_token"), owner["transfer_token"])
    self.assertNotEqual(tender.get("owner_token"), owner["owner_token"])

    # time
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": time}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertNotEqual(tender.get("awardPeriod", {}).get("endDate"), time["awardPeriod"]["endDate"])
    self.assertNotEqual(tender.get("date"), time["date"])
    self.assertNotEqual(tender.get("dateModified"), time["dateModified"])

    # lists
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": lists}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender.get("revisions", []), [])
    self.assertEqual(tender.get("plans", []), [])
    self.assertEqual(tender.get("cancellations", []), [])


def create_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

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

    for kind in PQ_KINDS:
        data = deepcopy(self.initial_data)
        data['procuringEntity']['kind'] = kind
        response = self.app.post_json("/tenders", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json['data']['procuringEntity']['kind'],
            kind
        )


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(
        set(tender) - set(self.initial_data),
        set(
            [
                u"id",
                u"dateModified",
                u"tenderID",
                u"date",
                u"status",
                u"awardCriteria",
                u"submissionMethod",
                u"owner",
            ]
        ),
    )
    self.assertIn(tender["id"], response.headers["Location"])


def patch_tender(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = u"0440000000"
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")

    
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"milestones": test_milestones}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{
            u"description": [u"Milestones are not applicable to pricequotation"],
            u"location": u"body",
            u"name": u"milestones"
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procuringEntity": {"kind": "defense"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"]["kind"], "defense")
    tender[u"procuringEntity"]['kind'] = u"defense"

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": {"contactPoint": {"faxNumber": None}}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("faxNumber", response.json["data"]["procuringEntity"]["contactPoint"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": {"contactPoint": {"faxNumber": u"0440000000"}}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("startDate", response.json["data"]["tenderPeriod"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    new_dateModified = new_tender.pop("dateModified")
    tender[u"procurementMethodRationale"] = u"Open"
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

    revisions = self.db.get(tender["id"]).get("revisions")
    self.assertEqual(revisions[-1][u"changes"][0]["op"], u"remove")
    self.assertEqual(revisions[-1][u"changes"][0]["path"], u"/procurementMethodRationale")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [{}, data["items"][0]]}}
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
        {"data": {"guarantee": {"amount": 12, "valueAddedTaxIncluded": True}}},
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

    # response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.auction'}})
    # self.assertEqual(response.status, '200 OK')

    # response = self.app.get('/tenders/{}'.format(tender['id']))
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')

    tender_data = self.db.get(tender["id"])
    tender_data["status"] = "complete"
    self.db.save(tender_data)


@mock.patch("openprocurement.tender.core.models.CANT_DELETE_PERIOD_START_DATE_FROM", get_now() - timedelta(days=1))
def required_field_deletion(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

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
                u"description": {u"startDate": [u"This field cannot be deleted"]},
                u"location": u"body",
                u"name": u"tenderPeriod",
            }
        ],
    )


def tender_Administrator_change(self):
    self.create_tender()
    self.set_status('active.tendering')
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reasonType": "noDemand",
        "status": "active",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"mode": u"test"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], u"test")


def patch_tender_by_pq_bot(self):
    response = self.app.post_json("/tenders", {"data": deepcopy(self.initial_data)})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender = response.json["data"]

    self.assertEqual(tender["status"], "draft")
    self.assertEqual(len(tender["items"]), 1)
    self.assertNotIn("shortlistedFirms", tender)
    self.assertNotIn("classification", tender["items"][0])
    self.assertNotIn("unit", tender["items"][0])

    data = {"data": {
        "status": "draft.publishing",
        "profile": test_short_profile["id"]}
    }
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data)
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.publishing")
    self.assertEqual(tender["profile"], test_short_profile["id"])

    items = deepcopy(tender["items"])
    items[0]["classification"] = test_short_profile["classification"]
    items[0]["unit"] = test_short_profile["unit"]
    amount = sum([item["quantity"] for item in items]) * test_short_profile["value"]["amount"]
    value = deepcopy(test_short_profile["value"])
    value["amount"] = amount
    criteria = deepcopy(test_short_profile["criteria"])
    data = {
        "data": {
            "status": "active.tendering",
            "items": items,
            "shortlistedFirms": test_shortlisted_firms,
            "criteria": criteria,
            "value": value
        }
    }

    # try to patch by user
    for patch in ({'data': {'status': 'active.tendering'}}, data):
        with change_auth(self.app, ("Basic", ("broker", ""))) as app:
            resp = app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), patch, status=403)
            self.assertEqual(resp.status, "403 Forbidden")
            self.assertEqual(resp.json['status'], "error")
            self.assertEqual(resp.json['errors'], [
                {'description': "tender_owner can't switch tender from status (draft.publishing) to (active.tendering)",
                 'location': 'body',
                 'name': 'data'}
            ])

    # patch by bot
    with change_auth(self.app, ("Basic", ("pricequotation", ""))) as app:
        resp = app.patch_json("/tenders/{}".format(tender_id), data)
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], data["data"]["status"])
    self.assertIn("classification", tender["items"][0])
    self.assertIn("unit", tender["items"][0])
    self.assertEqual(len(tender["shortlistedFirms"]), len(test_shortlisted_firms))
    self.assertEqual(len(tender["criteria"]), len(test_short_profile["criteria"]))
    self.assertEqual(tender["value"], value)

    # switch tender to `draft.unsuccessful`
    response = self.app.post_json("/tenders", {"data": deepcopy(self.initial_data)})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender = response.json["data"]

    self.assertEqual(tender["status"], "draft")
    self.assertEqual(len(tender["items"]), 1)
    self.assertNotIn("shortlistedFirms", tender)
    self.assertNotIn("classification", tender["items"][0])
    self.assertNotIn("unit", tender["items"][0])

    data = {"data": {"status": "draft.publishing", "profile": "a1b2c3-a1b2c3e4-f1g2i3-h1g2k3l4"}}
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "profile", "description": ["The profile value doesn't match id pattern"]}]
    )

    # set not existed profile id
    data["data"]["profile"] = "123456-12345678-123456-12345678"
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data)
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.publishing")
    self.assertEqual(tender["profile"], "123456-12345678-123456-12345678")

    with change_auth(self.app, ("Basic", ("pricequotation", ""))) as app:
        self.app.patch_json(
            "/tenders/{}".format(tender_id),
            {"data": {"status": "draft.unsuccessful", "unsuccessfulReason": ["Profile not found in catalogue"]}}
        )

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.unsuccessful")
    self.assertEqual(tender["unsuccessfulReason"], ["Profile not found in catalogue"])
    self.assertNotIn("classification", tender["items"][0])
    self.assertNotIn("unit", tender["items"][0])
    self.assertNotIn("shortlistedFirms", tender)

# TenderProcessTest


def invalid_tender_conditions(self):
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token =  response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # cancellation
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "reasonType": "noDemand",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    response = self.app.post(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation_id, owner_token),
        {"data": {"status": "active"}},
    )

    # check status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_valid_bid_tender(self):
    tender_id = self.tender_id
    owner_token = self.tender_token
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    resp = self.app.post_json(
        "/tenders/{}/bids".format(tender_id), {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_requirement_response_valid
        }}
    )
    token = resp.json['access']['token']
    # switch to active.qualification
    self.set_status("active.qualification")
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, token),
        {"data": {"status": "active"}}
    )
    self.assertNotEqual(response.json["data"]["date"], award_date)

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]
    # after stand slill period
    self.set_status("active.awarded", 'end')
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
    tender_id = self.tender_id
    owner_token = self.tender_token
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    resp = self.app.post_json(
        "/tenders/{}/bids".format(tender_id), {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": test_requirement_response_valid}}
    )
    token = resp.json['access']['token']
    # switch to active.qualification
    self.set_status('active.tendering', 'end')
    resp = self.check_chronograph()
    self.assertEqual(resp.json['data']['status'], 'active.qualification')
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, token),
        {"data": {"status": "unsuccessful"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    tender_id =  self.tender_id
    owner_token = self.tender_token
    # create bid
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 450},
            "requirementResponses": test_requirement_response_valid
        }}
    )
    bid_1 = response.json["data"]["id"]
    bid_token1 = response.json["access"]["token"]

    # create second bid
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 300},
            "requirementResponses": test_requirement_response_valid
        }}
    )
    bid_2 = response.json["data"]["id"]
    bid_token2 = response.json["access"]["token"]
    self.set_status('active.tendering', 'end')
    resp = self.check_chronograph()
    self.assertEqual(resp.json['data']['status'], 'active.qualification')
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award_id = award['id']
    self.assertEqual(award['bid_id'], bid_2)
    self.assertEqual(award['value']['amount'], 300)
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, bid_token2),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award2_id = award['id']
    self.assertEqual(award['bid_id'], bid_1)
    self.assertEqual(award['value']['amount'], 450)
    self.assertNotEqual(award_id, award2_id)

    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, bid_token1),
        {"data": {"status": "active"}}
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
    tender_id = self.tender_id
    owner_token = self.tender_token
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    resp = self.app.post_json(
        "/tenders/{}/bids".format(tender_id), {"data": {
            "tenderers": [test_organization],
            "value": {"amount": 500},
            "requirementResponses": test_requirement_response_valid
        }}
    )
    token = resp.json['access']['token']
    # switch to active.qualification
    self.set_status("active.tendering", 'end')
    resp = self.check_chronograph().json
    self.assertEqual(resp['data']['status'], 'active.qualification')

    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, token), {"data": {"status": "active"}}
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


