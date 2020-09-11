# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from iso8601 import parse_date

from openprocurement.api.constants import SANDBOX_MODE, CPV_ITEMS_CLASS_FROM, ROUTE_PREFIX
from openprocurement.api.utils import get_now


from openprocurement.tender.belowthreshold.tests.base import test_organization

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE, FEATURES_MAX_SUM
from openprocurement.tender.competitivedialogue.models import CompetitiveDialogUA, CompetitiveDialogEU
from openprocurement.tender.competitivedialogue.tests.base import test_bids


# CompetitiveDialogTest
from openprocurement.tender.core.utils import calculate_tender_business_date


def simple_add_tender_ua(self):
    u = CompetitiveDialogUA(self.test_tender_data_ua)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == CD_UA_TYPE

    u.delete_instance(self.db)


def simple_add_tender_eu(self):
    u = CompetitiveDialogEU(self.test_tender_data_eu)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == CD_EU_TYPE

    u.delete_instance(self.db)


# CompetitiveDialogEUResourceTest
def create_tender_invalid_eu(self):
    """
      Try create invalid tender
    """
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
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "value": "invalid_value"}}, status=422
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
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "procurementMethod": "invalid_value"}}, status=422
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
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"value"}, response.json["errors"]
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": CD_EU_TYPE, "enquiryPeriod": {"endDate": "invalid_value"}}},
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
        {"data": {"procurementMethodType": CD_EU_TYPE, "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"}}},
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


def create_tender_generated_eu(self):
    """
      Try create tender with our id, doc_id, tenderID
    """
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
        {
            u"procurementMethodType",
            u"id",
            u"dateModified",
            u"tenderID",
            u"status",
            u"enquiryPeriod",
            u"tenderPeriod",
            u"complaintPeriod",
            u"items",
            u"value",
            u"owner",
            u"procuringEntity",
            u"next_check",
            u"procurementMethod",
            u"awardCriteria",
            u"submissionMethod",
            u"title",
            u"title_en",
            u"date",
            u"minimalStep",
            u"mainProcurementCategory",
            u"milestones",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])


def patch_tender(self):
    """
      Try edit tender
    """
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

    self.set_status("complete")

    # Can't set activate.action status anytime for dialog
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [
            u"Value must be one of ['draft', 'active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.stage2.pending', 'active.stage2.waiting', 'complete', 'cancelled', 'unsuccessful']."
        ],
    )


def multiple_bidders_tender_eu(self):
    # create tender
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    # create bids
    bidder_data = deepcopy(test_organization)
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_bids[0])
    bid_data["value"] = {"amount": 500}
    bid_data["tenderers"] = [bidder_data]
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bid_data["value"]["amount"] = 499
    bidder_data["identifier"]["id"] = u"00037257"
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    bid_data["value"]["amount"] = 498
    bidder_data["identifier"]["id"] = u"00037259"
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "active.pre-qualification"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    # list qualifications
    response = self.app.get("/tenders/{}/qualifications".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 3)
    # approve first two bids qualification/bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[0]["id"], tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[1]["id"], tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # cancel qualification for second bid
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[1]["id"], tender_owner_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("Location", response.headers)
    new_qualification_location = response.headers["Location"]
    qualification_id = new_qualification_location[-32:]
    # approve the bid again
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualification_id, tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # try to change tender state by chronograph leaving one bid unreviewed
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    # approve third bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[2]["id"], tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to next status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    # ensure that tender has been switched to "active.pre-qualification.stand-still"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    # time traver
    self.set_status("active.stage2.pending", {"id": tender_id, "status": "active.pre-qualification.stand-still"})
    # change tender state
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.stage2.pending")

    # get auction info
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{tender_id}?acc_token={token}".format(tender_id=tender_id, token=tender_owner_token),
        {"data": {"status": "active.stage2.waiting"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.stage2.waiting")


def try_go_to_ready_stage_eu(self):
    # create tender
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    # create bids
    bid_data = deepcopy(test_bids[0])
    bid_data["value"] = {"amount": 500}
    bidder_data = deepcopy(test_organization)
    bid_data["tenderers"] = [bidder_data]
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bid_data["value"]["amount"] = 499
    bidder_data["identifier"]["id"] = u"00037257"
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    bid_data["value"]["amount"] = 498
    bidder_data["identifier"]["id"] = u"00037258"
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # tender should switch to "active.pre-qualification"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    # list qualifications
    response = self.app.get("/tenders/{}/qualifications".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 3)
    # approve first two bids qualification/bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[0]["id"], tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[1]["id"], tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # cancel qualification for second bid
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[1]["id"], tender_owner_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("Location", response.headers)
    new_qualification_location = response.headers["Location"]
    qualification_id = new_qualification_location[-32:]
    # approve the bid again
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualification_id, tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # try to change tender state by chronograph leaving one bid unreviewed
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    # reject third bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[2]["id"], tender_owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to next status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    # ensure that tender has been switched to "active.pre-qualification.stand-still"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # get auction info
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{tender_id}?acc_token={token}".format(tender_id=tender_id, token=tender_owner_token),
        {"data": {"status": "active.stage2.waiting"}},
    )
    self.assertEqual(response.status, "200 OK")

    # ensure that tender has been switched to "active.pre-qualification.stand-still"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")


# CompetitiveDialogUAResourceTest
def create_tender_invalid_ua(self):
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
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "value": "invalid_value"}}, status=422
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
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "procurementMethod": "invalid_value"}}, status=422
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
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"value"}, response.json["errors"]
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": CD_UA_TYPE, "enquiryPeriod": {"endDate": "invalid_value"}}},
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
        {"data": {"procurementMethodType": CD_UA_TYPE, "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"}}},
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


def create_tender_generated_ua(self):
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
                u"items",
                u"value",
                u"procuringEntity",
                u"next_check",
                u"procurementMethod",
                u"awardCriteria",
                u"submissionMethod",
                u"title",
                u"owner",
                u"date",
                u"minimalStep",
                u"mainProcurementCategory",
                u"milestones",
            ]
        ),
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])


def patch_tender_1(self):
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
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
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

    # Can't set activate.action status anytime for dialog
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [
            u"Value must be one of ['draft', 'active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.stage2.pending', 'active.stage2.waiting', 'complete', 'cancelled', 'unsuccessful']."
        ],
    )


def update_status_complete_owner_ua(self):
    """
    Try update dialog status by owner, when it's complete
    """
    # Create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    self.set_status("complete")

    response = self.app.get("/tenders/{tender_id}".format(tender_id=self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "complete")
    response = self.app.patch_json(
        "/tenders/{tender_id}?acc_token={token}".format(tender_id=self.tender_id, token=token),
        {"data": {"status": "active.pre-qualification"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


# CompetitiveDialogEUResourceTest
def patch_tender_eu_ua(self):
    """
      Can't modify tender if tenderPeriod.endDate < 7 days, before action
    """

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")
    self.tender_id = tender["id"]
    self.set_enquiry_period_end()

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
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"guarantee": {"currency": "USD"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")


def path_complete_tender(self):
    """
      Try update dialog when status is complete
    """
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.set_status("complete")
    response = self.app.patch_json(
        "/tenders/{tender_id}?acc_token={token}".format(tender_id=tender["id"], token=owner_token),
        {"data": {"guarantee": None}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def tender_features_invalid(self):
    """
      Try create invalid features
    """
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

    data["features"][1]["code"] = u"OCDS-123454-YEARS"
    data["features"][1]["enum"][0]["value"] = 0.3
    data["features"].append(data["features"][0].copy())
    data["features"][2]["code"] = u"OCDS-123455-YEARS"
    data["features"][2]["enum"][0]["value"] = 0.3
    data["features"].append(data["features"][0].copy())
    data["features"][3]["code"] = u"OCDS-123456-YEARS"
    data["features"][3]["enum"][0]["value"] = 0.3
    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    u"Sum of max value of all features should be less then or equal to {:.0f}%".format(
                        FEATURES_MAX_SUM * 100
                    )
                ],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )


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
                "description": ["Value must be one of ['services', 'works']."],
            }
        ],
    )

    # test success creation
    data["mainProcurementCategory"] = "services"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")

    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update tender in active.tendering status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "works"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "works")
