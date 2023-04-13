from unittest.mock import patch
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import CPV_ITEMS_CLASS_FROM, TZ
from openprocurement.api.utils import get_now, parse_date

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_lots
from openprocurement.tender.core.tests.utils import change_auth

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE, FEATURES_MAX_SUM
from openprocurement.tender.competitivedialogue.tests.base import test_tender_cd_stage1_bids
from openprocurement.tender.core.utils import calculate_tender_business_date


# CompetitiveDialogEUResourceTest
def create_tender_invalid_eu(self):
    """
      Try create invalid tender
    """
    request_path = "/tenders"

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_EU_TYPE, "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
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
                "description": ["Please use a mapping for this field or Value instance instead of str."],
                "location": "body",
                "name": "value",
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
            "description": ["Value must be one of ['open', 'selective', 'limited']."],
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
        {"description": ["This field is required."], "location": "body", "name": "value"}, response.json["errors"]
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
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
                "description": {"endDate": ["Could not parse invalid_value. Should be ISO8601."]},
                "location": "body",
                "name": "enquiryPeriod",
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
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
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
        [{"description": ["CPV class of items should be identical"],
          "location": "body", "name": "items"}],
    )

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"deliveryDate": ["This field is required."]}], "location": "body", "name": "items"}],
    )


def create_tender_generated_eu(self):
    """
      Try create tender with our id, doc_id, tenderID
    """
    data = self.initial_data.copy()
    # del data['awardPeriod']
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
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
            "value",
            "owner",
            "procuringEntity",
            "next_check",
            "procurementMethod",
            "awardCriteria",
            "title",
            "title_en",
            "date",
            "minimalStep",
            "mainProcurementCategory",
            "milestones",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])


def patch_tender(self):
    """
      Try edit tender
    """
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
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "dateModified",
            "description": "Rogue field"
        }]
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
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [item0]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    item = deepcopy(item0)
    item["classification"]["id"] = "55523100-3"
    item["classification"]["description"] = "Послуги з харчування у школах"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [item]
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(item0)
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

    item = deepcopy(item0)
    item["additionalClassifications"] = tender["items"][0]["additionalClassifications"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_dateModified2 = response.json["data"]["dateModified"]

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

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"currency": "USD", "amount": 12}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    self.set_status("active.stage2.waiting")

    with change_auth(self.app, ("Basic", ("competitive_dialogue", ""))):
        self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
            {"data": {"stage2TenderID": "a" * 32, "id": tender["id"]}}
        )
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
            {"data": {"status": "complete"}}
        )

    self.assertEqual(response.json["data"]["status"], "complete")
    self.assertEqual(response.json["data"]["stage2TenderID"], "a" * 32)

    # Can't set activate.action status anytime for dialog
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"status": "active.auction"}},
        status=403
    )


def multiple_bidders_tender_eu(self):
    # create tender
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # create bids
    bidder_data = deepcopy(test_tender_below_organization)
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(test_tender_cd_stage1_bids[0])
    bid_data["tenderers"] = [bidder_data]
    self.create_bid(tender_id, bid_data, "pending")
    bidder_data["identifier"]["id"] = "00037257"
    self.create_bid(tender_id, bid_data, "pending")
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    bidder_data["identifier"]["id"] = "00037259"
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
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
    response = self.check_chronograph()
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
    response = self.check_chronograph()
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
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # create bids
    bid_data = deepcopy(test_tender_cd_stage1_bids[0])
    bidder_data = deepcopy(test_tender_below_organization)
    bid_data["tenderers"] = [bidder_data]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")
    bidder_data["identifier"]["id"] = "00037257"
    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]
    bidder_data["identifier"]["id"] = "00037258"
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
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
    response = self.check_chronograph()
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


# CompetitiveDialogUAResourceTest
def create_tender_invalid_ua(self):
    request_path = "/tenders"

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": CD_UA_TYPE, "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
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
                "description": ["Please use a mapping for this field or Value instance instead of str."],
                "location": "body",
                "name": "value",
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
            "description": ["Value must be one of ['open', 'selective', 'limited']."],
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
        {"description": ["This field is required."], "location": "body", "name": "value"}, response.json["errors"]
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
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
                "description": {"endDate": ["Could not parse invalid_value. Should be ISO8601."]},
                "location": "body",
                "name": "enquiryPeriod",
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
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
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
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
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
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
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
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
    )

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]["endDate"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"deliveryDate": {"endDate": ["This field is required."]}}],
                "location": "body",
                "name": "items",
            }
        ],
    )


def create_tender_generated_ua(self):
    data = self.initial_data.copy()
    # del data['awardPeriod']
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
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
            "value",
            "procuringEntity",
            "next_check",
            "procurementMethod",
            "awardCriteria",
            "title",
            "owner",
            "date",
            "minimalStep",
            "mainProcurementCategory",
            "milestones",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])


def patch_tender_1(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    self.tender_id = tender["id"]
    dateModified = tender.pop("dateModified")

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"status": "cancelled"}},
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
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procurementMethodRationale": "Open"}}
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
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "dateModified",
            "description": "Rogue field"
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

    data = deepcopy(item0)
    data["classification"] = {"scheme": "ДК021", "id": "44620000-2", "description": "Cartons 2"}
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [data]}},
        status=200,
    )

    data["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [data]
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't change classification")

    data = deepcopy(item0)
    data["additionalClassifications"] = [tender["items"][0]["additionalClassifications"][0] for i in range(3)]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [data]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    data = deepcopy(item0)
    data["additionalClassifications"] = tender["items"][0]["additionalClassifications"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [data]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_dateModified2 = response.json["data"]["dateModified"]

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

    self.set_status("complete")

    # Can't set activate.action status anytime for dialog
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"status": "active.auction"}},
        status=403
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update tender in current (complete) status",
    )


def update_status_complete_owner_ua(self):
    """
    Try update dialog status by owner, when it's complete
    """
    # Create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
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
@patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
       get_now() + timedelta(days=1))
def patch_tender_eu_ua(self):
    """
      Can't modify tender if tenderPeriod.endDate < 7 days, before action
    """
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.set_enquiry_period_end()

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"value": {"amount": 501, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 7 days")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    tender = response.json["data"]

    tender_period_end_date = (calculate_tender_business_date(
        get_now(), timedelta(days=7), tender
    ) + timedelta(seconds=1)).astimezone(TZ)
    enquiry_period_end_date = calculate_tender_business_date(
        tender_period_end_date, -timedelta(days=10), tender
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "value": {"amount": 501, "currency": "UAH"},
                "tenderPeriod": {
                    "startDate": tender["tenderPeriod"]["startDate"],
                    "endDate": tender_period_end_date.isoformat(),
                },
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
        {"description": {"valueAddedTaxIncluded": "Rogue field"}, "location": "body", "name": "guarantee"},
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"currency": "USD", "amount": 12}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")


def path_complete_tender(self):
    """
      Try update dialog when status is complete
    """
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
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
    data["features"][0]["enum"][0]["value"] = 1.0
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": [{"value": ["Float value should be less than 0.99."]}]}],
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
    data["features"][1]["enum"][0]["value"] = 0.3
    data["features"].append(data["features"][0].copy())
    data["features"][2]["code"] = "OCDS-123455-YEARS"
    data["features"][2]["enum"][0]["value"] = 0.3
    data["features"].append(data["features"][0].copy())
    data["features"][3]["code"] = "OCDS-123456-YEARS"
    data["features"][3]["enum"][0]["value"] = 0.3
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "Sum of max value of all features should be less then or equal to {:.0f}%".format(
                        FEATURES_MAX_SUM * 100
                    )
                ],
                "location": "body",
                "name": "features",
            }
        ],
    )


def patch_tender_lots_none(self):
    data = deepcopy(self.initial_data)

    set_tender_lots(data, self.test_lots_data)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]
    self.token_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token),
        {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {"location": "body", "name": "lots", "description": [["This field is required."]]},
            ],
        },
    )


def tender_with_main_procurement_category(self):
    data = dict(**self.initial_data)

    # test fail creation
    data["mainProcurementCategory"] = "whiskey,tango,foxtrot"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
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
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")
    self.set_initial_status(response.json)

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
