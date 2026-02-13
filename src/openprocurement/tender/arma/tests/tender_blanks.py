from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.constants import MILESTONE_CODES, MILESTONE_TITLES
from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.tests.base import test_signer_info
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_buyer,
    test_tender_below_supplier,
)
from openprocurement.tender.core.tests.utils import activate_contract, set_bid_lotvalues
from openprocurement.tender.core.utils import calculate_tender_full_date

# TenderResourceTest


def create_tender_invalid(self):
    request_path = "/tenders"

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

    self.app.post_json(request_path, {"data": {"procurementMethodType": "invalid_value"}}, status=404)

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": COMPLEX_ASSET_ARMA, "invalid_field": "invalid_value"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": COMPLEX_ASSET_ARMA, "value": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Please use a mapping for this field or PostEstimatedValue instance instead of str."],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": COMPLEX_ASSET_ARMA, "procurementMethod": "invalid_value"}},
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
        {"data": {"procurementMethodType": COMPLEX_ASSET_ARMA, "enquiryPeriod": {"endDate": "invalid_value"}}},
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
                "procurementMethodType": COMPLEX_ASSET_ARMA,
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

    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2014-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
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
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
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
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    self.initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=35)).isoformat(),
        "endDate": (now + timedelta(days=35)).isoformat(),
    }
    self.initial_data["awardPeriod"] = {
        "startDate": (now + timedelta(days=34)).isoformat(),
        "endDate": (now + timedelta(days=34)).isoformat(),
    }
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    del self.initial_data["auctionPeriod"]
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after auctionPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    data = {"amount": 15, "currency": "UAH"}
    self.initial_data["minimalStep"] = {"amount": "100.0", "valueAddedTaxIncluded": False}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Tender minimal step valueAddedTaxIncluded should be identical to tender valueAddedTaxIncluded",
                "location": "body",
                "name": "minimalStep.valueAddedTaxIncluded",
            }
        ],
    )

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "100.0", "currency": "USD"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Tender minimal step currency should be identical to tender currency",
                "location": "body",
                "name": "minimalStep.currency",
            }
        ],
    )
    data = self.initial_data["items"][0].pop("additionalClassifications")
    cpv_code = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(
        request_path,
        {
            "data": self.initial_data,
            "config": self.initial_config,
        },
        status=201,
    )
    self.initial_data["items"][0]["additionalClassifications"] = data
    self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    data = self.initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    cpv_code = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = data
    self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
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
                "description": {"contactPoint": {"telephone": ["wrong telephone format (could be missed +)"]}},
                "location": "body",
                "name": "procuringEntity",
            }
        ],
    )

    data = self.initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = "19212310-1"
    data["classification"] = classification
    item = deepcopy(self.initial_data["items"][0])
    self.initial_data["items"] = [item, data]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items (1921, 4461) should be identical"], "location": "body", "name": "items"}],
    )

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"deliveryDate": ["This field is required."]}], "location": "body", "name": "items"}],
    )


def create_tender_generated(self):
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
            "enquiryPeriod",
            "items",
            "tenderPeriod",
            "awardCriteria",
            "dateModified",
            "submissionMethod",
            "next_check",
            "procurementMethod",
            "procurementMethodType",
            "owner",
            "documents",
            "id",
            "title_en",
            "qualificationPeriod",
            "lots",
            "title",
            "dateCreated",
            "mainProcurementCategory",
            "contractChangeRationaleTypes",
            "procuringEntity",
            "noticePublicationDate",
            "tenderID",
            "value",
            "date",
            "criteria",
            "status",
        },
    )
    self.assertNotEqual(data["id"], tender["id"])


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    item_id = tender["items"][0]["id"]
    self.tender_id = response.json["data"]["id"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "tenderPeriod": {
                    "startDate": tender["enquiryPeriod"]["endDate"],
                    "endDate": tender["tenderPeriod"]["endDate"],
                }
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "tenderPeriod",
                "description": ["tenderPeriod must be at least 20 full business days long"],
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("invalidationDate", response.json["data"]["enquiryPeriod"])
    new_tender = response.json["data"]
    new_tender.pop("enquiryPeriod")
    new_dateModified = new_tender.pop("dateModified")
    tender.pop("enquiryPeriod")
    tender["procurementMethodRationale"] = "Open"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertTrue(
        any(i for i in revisions[-1]["changes"] if i["op"] == "remove" and i["path"] == "/procurementMethodRationale")
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
    )

    pq_entity = tender["procuringEntity"]
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": "Can't change procuringEntity.kind in a public tender",
            }
        ],
    )

    item = deepcopy(self.initial_data["items"][0])
    item["id"] = item_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(self.initial_data["items"][0])
    item["id"] = item_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [{**item, "id": item_id}, {**item, "id": uuid4().hex}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)
    new_dateModified2 = response.json["data"]["dateModified"]

    items = deepcopy(self.initial_data["items"])
    items[0]["id"] = item_id
    items[0]["classification"]["id"] = "55523100-3"
    items[0]["classification"]["description"] = "Послуги з харчування у школах"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": items}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0],
        {"description": ["Can't change classification group of items"], "location": "body", "name": "items"},
    )

    items = deepcopy(self.initial_data["items"])
    items[0]["id"] = item_id
    items[0]["additionalClassifications"] = [tender["items"][0]["additionalClassifications"][0] for i in range(3)]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    items = deepcopy(self.initial_data["items"])
    items[0]["id"] = item_id
    items[0]["additionalClassifications"] = tender["items"][0]["additionalClassifications"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    period = {
        "startDate": calculate_tender_full_date(
            parse_date(new_dateModified2),
            -timedelta(3),
            tender=None,
            working_days=True,
        ).isoformat(),
        "endDate": new_dateModified2,
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

    self.set_status("active.tendering")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def patch_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    tender_period = tender["tenderPeriod"]
    tender_period["startDate"] = (parse_date(tender_period["startDate"]) + timedelta(days=1)).isoformat()
    tender_period["endDate"] = (parse_date(tender_period["endDate"]) + timedelta(days=1)).isoformat()

    item = deepcopy(tender["items"][0])
    item.update(description="test item", quantity=20, id="0" * 32)
    tender_patch_data = {
        "items": [item],
        "tenderPeriod": tender_period,
    }

    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        if "items" in agreement:
            agreement["items"] = [item]
        self.mongodb.agreements.save(agreement)

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": tender_patch_data})

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("items", tender)
    self.assertEqual(len(tender["items"]), 1)
    self.assertEqual(tender["items"][0]["description"], "test item")

    self.assertEqual(tender["tenderPeriod"], tender_period)
    tender_patch_data = {
        "features": [
            {
                "title": "test feature",
                "relatedItem": "0" * 32,
                "enum": [{"value": 0.1, "title": "test feature value"}],
            }
        ],
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": tender_patch_data}, status=422
    )
    self.assertCountEqual(
        response.json["errors"], [{"location": "body", "name": "features", "description": "Rogue field"}]
    )


def set_buyers_signer_info(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["procuringEntity"].pop("signerInfo", None)

    buyer = deepcopy(test_tender_below_buyer)
    buyer["id"] = uuid4().hex
    buyer.pop("signerInfo", None)

    tender_data["buyers"] = [buyer]
    tender_data["items"][0]["relatedBuyer"] = buyer["id"]

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("signerInfo", response.json["data"]["procuringEntity"])
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "contractTemplateName": "00000000.0002.01",
            }
        },
        status=422,
    )
    self.assertCountEqual(
        response.json["errors"],
        [{"description": "Rogue field", "location": "body", "name": "contractTemplateName"}],
    )

    tender_data["buyers"][0]["signerInfo"] = test_signer_info

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "buyers": tender_data["buyers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["buyers"][0]["signerInfo"], test_signer_info)


def set_procuring_entity_signer_info(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["procuringEntity"].pop("signerInfo", None)

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("signerInfo", response.json["data"]["procuringEntity"])
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "contractTemplateName": "00000000.0002.01",
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": "Rogue field", "location": "body", "name": "contractTemplateName"}],
    )

    tender_data["procuringEntity"]["signerInfo"] = test_signer_info

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "procuringEntity": tender_data["procuringEntity"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["procuringEntity"]["signerInfo"], test_signer_info)


def invalid_bid_tender_lot(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    for lot in self.test_lots_data * 2:
        response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": lot})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/lots?acc_token={}".format(tender_id, owner_token))
    lots = response.json["data"]
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data.update(
        {
            "lotValues": [{"value": self.test_bids_data[0]["value"], "relatedLot": i["id"]} for i in lots],
        }
    )

    self.create_bid(tender_id, bid_data, "pending")

    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(tender_id, lots[1]["id"], owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


# TenderProcessTest


def one_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    self.set_initial_status(response.json)
    # create bid
    bidder_data = deepcopy(test_tender_below_supplier)
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [bidder_data]

    set_bid_lotvalues(bid_data, response.json["data"]["lots"])
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    # tender should switch to "unsuccessful"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def unsuccessful_after_prequalification_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # create bid
    bidder_data = deepcopy(test_tender_below_supplier)
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [bidder_data]

    for i in range(3):
        set_bid_lotvalues(bid_data, response.json["data"]["lots"])
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
    # disqualify all bids
    self.app.authorization = ("Basic", ("broker", ""))
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualification["id"], owner_token),
            {"data": {"status": "unsuccessful"}},
        )
        self.assertEqual(response.status, "200 OK")
    # switch to next status
    self.add_sign_doc(tender_id, owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    visible_fields = {
        "id",
        "status",
        "tenderers",
        "selfQualified",
        "lotValues",
    }
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        visible_fields.add("selfEligible")
    else:
        visible_fields.add("requirementResponses")

    for bid in response.json["data"]["bids"]:
        self.assertEqual(bid["status"], "unsuccessful")
        self.assertEqual(set(bid.keys()), visible_fields)
        for lot_value in bid["lotValues"]:
            self.assertEqual(lot_value["status"], "unsuccessful")
            self.assertNotIn("value", lot_value)


def one_qualificated_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # create bids
    bidder_data = deepcopy(test_tender_below_supplier)
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [bidder_data]

    set_bid_lotvalues(bid_data, response.json["data"]["lots"])
    self.create_bid(tender_id, bid_data, "pending")

    bid_data["lotValues"][0]["value"] = self.test_bids_data[1]["value"]
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
    self.assertEqual(len(qualifications), 2)
    # approve first qualification/bid
    self.app.authorization = None
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}".format(tender_id, qualifications[0]["id"]),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}".format(tender_id, qualifications[0]["id"]),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[0]["id"], "c" * 32),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[0]["id"], tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # bid should be activated
    response = self.app.get("/tenders/{}/bids/{}".format(tender_id, qualifications[0]["bidID"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # invalidate second qualification/bid
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[1]["id"], tender_owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # bid should be cancelled
    response = self.app.get("/tenders/{}/bids/{}".format(tender_id, qualifications[1]["bidID"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotIn("value", response.json["data"])
    # switch to next status
    self.add_sign_doc(tender_id, tender_owner_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    # tender should switch to "unsuccessful"
    self.set_status("active.auction", {"id": tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    # ensure that tender has been switched to "unsuccessful"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def multiple_bidders_tender(self):
    # create tender
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    tender = response.json["data"]
    self.set_initial_status(response.json)
    # create bids
    bidder_data = deepcopy(test_tender_below_supplier)

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [bidder_data]

    self.app.authorization = ("Basic", ("broker", ""))
    set_bid_lotvalues(bid_data, tender["lots"])
    self.create_bid(tender_id, bid_data, "pending")

    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]

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
    self.add_sign_doc(tender_id, tender_owner_token, document_type="evaluationReports")
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

    response = self.check_chronograph()
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, tender["lots"][0]["id"]),
        {
            "data": {
                "lots": [{"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in tender["lots"]],
                "bids": [
                    {
                        "id": i["id"],
                        "lotValues": [
                            {
                                "relatedLot": j["relatedLot"],
                                "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"]),
                            }
                            for j in i["lotValues"]
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
        "/tenders/{}/auction/{}".format(tender_id, tender["lots"][0]["id"]),
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": lot["relatedLot"]} for lot in b["lotValues"]]}
                    for b in auction_bids_data
                ]
            }
        },
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, tender_owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, tender_owner_token, docs_url=f"/awards/{award_id}/documents")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, tender_owner_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, tender_owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    # set award as active
    self.add_sign_doc(tender_id, tender_owner_token, docs_url=f"/awards/{award2_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award2_id, tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]

    # XXX rewrite following part with less of magic actions
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("complete", {"status": "active.awarded"})
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, tender_owner_token, bid_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def lost_contract_for_active_award(self):
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["tenderers"] = [test_tender_below_supplier]

    self.app.authorization = ("Basic", ("broker", ""))
    set_bid_lotvalues(bid_data, response.json["data"]["lots"])
    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")
    # create bid #2
    self.app.authorization = ("Basic", ("broker", ""))
    _, bid2_token = self.create_bid(tender_id, bid_data, "pending")
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
    # approve qualification
    for qualification in qualifications:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.auction
    self.set_status("active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction".format(tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # lost contract
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender["contracts"]:
        self.mongodb.contracts.delete(i["id"])
    del tender["contracts"]
    self.mongodb.tenders.save(tender)
    # create lost contract
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contracts", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_delivery_milestones(self):
    lot_id = self.initial_lots[0]["id"] if self.initial_lots else None
    data = deepcopy(self.initial_data)
    data["milestones"] = [
        {
            "id": "a" * 32,
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 2, "type": "calendar"},
            "sequenceNumber": 1,
            "code": "standard",
            "percentage": 10,
            "relatedLot": lot_id,
        },
        {
            "id": "b" * 32,
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 2, "type": "calendar"},
            "sequenceNumber": 2,
            "code": "standard",
            "percentage": 90,
            "relatedLot": lot_id,
        },
    ]

    data["milestones"][-1]["duration"]["days"] = 1500
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"duration": ["days shouldn't be more than 1000 for delivery milestone"]}],
            }
        ],
    )

    data["milestones"][-1]["duration"]["days"] = 1000
    data["milestones"][-1]["code"] = "postpayment"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "code": [f"Value must be one of {MILESTONE_CODES['delivery']}"],
                    }
                ],
            }
        ],
    )

    data["milestones"][-1]["code"] = "standard"
    data["milestones"][-1]["title"] = "executionOfWorks"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"title": [f"Value must be one of {MILESTONE_TITLES['delivery']}"]}],
            }
        ],
    )

    data["milestones"][-1]["title"] = "signingTheContract"
    old_lot_id = data["milestones"][-1].pop("relatedLot")
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "relatedLot": "Related lot must be set in all milestones or all milestones should be related to tender"
                    }
                ],
            }
        ],
    )

    data["milestones"][-1]["relatedLot"] = old_lot_id
    old_percentage = data["milestones"][-1].pop("percentage")
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "milestones", "description": [{"percentage": ["This field is required."]}]}],
    )

    data["milestones"][-1]["percentage"] = 100
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": f"Sum of the delivery milestone percentages 110.0 is not equal 100 for lot {lot_id}.",
            }
        ],
    )
    data["milestones"][-1]["percentage"] = old_percentage
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")


def tender_financing_milestones(self):
    lot_id = self.initial_lots[0]["id"] if self.initial_lots else None
    data = deepcopy(self.initial_data)
    data["milestones"] = [
        {
            "id": "a" * 32,
            "title": "signingTheContract",
            "code": "prepayment",
            "type": "financing",
            "duration": {"days": 2, "type": "banking"},
            "sequenceNumber": 1,
            "percentage": 10,
            "relatedLot": lot_id,
        },
        {
            "id": "b" * 32,
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 999, "type": "calendar"},
            "sequenceNumber": 2,
            "percentage": 90,
            "relatedLot": lot_id,
        },
    ]

    data["milestones"][-1]["duration"]["days"] = 1500
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"duration": ["days shouldn't be more than 1000 for financing milestone"]}],
            }
        ],
    )

    data["milestones"][-1]["duration"]["days"] = 1000
    data["milestones"][-1]["code"] = "standard"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "code": [f"Value must be one of {MILESTONE_CODES['financing']}"],
                    }
                ],
            }
        ],
    )

    data["milestones"][-1]["code"] = "postpayment"
    data["milestones"][-1]["title"] = "afterPostPayment"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"title": [f"Value must be one of {MILESTONE_TITLES['financing']}"]}],
            }
        ],
    )

    data["milestones"][-1]["title"] = "signingTheContract"
    old_lot_id = data["milestones"][-1].pop("relatedLot")
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "relatedLot": "Related lot must be set in all milestones or all milestones should be related to tender"
                    }
                ],
            }
        ],
    )

    data["milestones"][-1]["relatedLot"] = old_lot_id
    old_percentage = data["milestones"][-1].pop("percentage")
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "milestones", "description": [{"percentage": ["This field is required."]}]}],
    )

    data["milestones"][-1]["percentage"] = 100
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": f"Sum of the financing milestone percentages 110.0 is not equal 100 for lot {lot_id}.",
            }
        ],
    )
    data["milestones"][-1]["percentage"] = old_percentage
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
