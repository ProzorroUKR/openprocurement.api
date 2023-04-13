# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from mock import patch

from openprocurement.api.utils import parse_date
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.api.constants import (
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    CPV_ITEMS_CLASS_FROM,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.tender.core.models import get_now
from openprocurement.tender.core.tests.criteria_utils import add_criteria


# TenderUATest
from openprocurement.tender.openuadefense.utils import calculate_tender_business_date


# TenderUAResourceTest
def create_tender_invalid(self):
    request_path = "/tenders"
    self.app.post_json(request_path, {"data": {"procurementMethodType": "invalid_value"}}, status=404)

    response = self.app.post_json(
        request_path,
        {"data": {"invalid_field": "invalid_value", "procurementMethodType": "aboveThresholdUA.defense"}},
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
        {"data": {"value": "invalid_value", "procurementMethodType": "aboveThresholdUA.defense"}},
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
        {"data": {"procurementMethod": "invalid_value", "procurementMethodType": "aboveThresholdUA.defense"}},
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
    # self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'enquiryPeriod'}, response.json['errors'])
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "value"}, response.json["errors"]
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"enquiryPeriod": {"endDate": "invalid_value"}, "procurementMethodType": "aboveThresholdUA.defense"}},
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
                "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"},
                "procurementMethodType": "aboveThresholdUA.defense",
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
    initial_data = deepcopy(self.initial_data)
    initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2014-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["tenderPeriod"] = data
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

    # data = self.initial_data['tenderPeriod']
    # self.initial_data['tenderPeriod'] = {'startDate': '2014-10-31T00:00:00', 'endDate': '2015-10-01T00:00:00'}
    # response = self.app.post_json(request_path, {'data': self.initial_data}, status=422)
    # self.initial_data['tenderPeriod'] = data
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [u'period should begin after enquiryPeriod'], u'location': u'body', u'name': u'tenderPeriod'}
    # ])

    now = get_now()
    initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    del initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=16)).isoformat(),
        "endDate": (now + timedelta(days=16)).isoformat(),
    }
    initial_data["awardPeriod"] = {
        "startDate": (now + timedelta(days=15)).isoformat(),
        "endDate": (now + timedelta(days=15)).isoformat(),
    }
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    del initial_data["auctionPeriod"]
    del initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after auctionPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    data = self.initial_data["minimalStep"]
    del self.initial_data["minimalStep"]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "minimalStep"},
        response.json["errors"],
    )

    data = initial_data["minimalStep"]
    initial_data["minimalStep"] = {"amount": "1000.0"}
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["value should be less than value of tender"],
                "location": "body",
                "name": "minimalStep",
            }
        ],
    )

    data = initial_data["minimalStep"]
    initial_data["minimalStep"] = {"amount": "100.0", "valueAddedTaxIncluded": False}
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender"
                ],
                "location": "body",
                "name": "minimalStep",
            }
        ],
    )

    data = initial_data["minimalStep"]
    initial_data["minimalStep"] = {"amount": "100.0", "currency": "USD"}
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["currency should be identical to currency of value of tender"],
                "location": "body",
                "name": "minimalStep",
            }
        ],
    )

    data = initial_data["items"][0].pop("additionalClassifications")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = initial_data["items"][0]["classification"]["id"]
        initial_data["items"][0]["classification"]["id"] = "99999999-9"
    status = 422 if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM else 201
    response = self.app.post_json(request_path, {"data": initial_data, "config": self.initial_config}, status=status)
    initial_data["items"][0]["additionalClassifications"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        initial_data["items"][0]["classification"]["id"] = cpv_code
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

    data = initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    initial_data["items"][0]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = initial_data["items"][0]["classification"]["id"]
        initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": initial_data, "config": self.initial_config}, status=422)
    initial_data["items"][0]["additionalClassifications"][0]["scheme"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        initial_data["items"][0]["classification"]["id"] = cpv_code
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

    data = test_tender_below_organization["contactPoint"]["telephone"]
    del initial_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {"data": initial_data, "config": self.initial_config}, status=422)
    initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
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
    correct_phone = initial_data["procuringEntity"]["contactPoint"]["telephone"]
    initial_data["procuringEntity"]["contactPoint"]["telephone"] = "++223"
    response = self.app.post_json(request_path, {"data": initial_data, "config": self.initial_config}, status=422)
    initial_data["procuringEntity"]["contactPoint"]["telephone"] = correct_phone
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

    data = initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = "19212310-1"
    data["classification"] = classification
    initial_data["items"] = [initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": initial_data, "config": self.initial_config}, status=422)
    initial_data["items"] = initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
    )

    data = deepcopy(initial_data)
    del data["items"][0]["deliveryDate"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"deliveryDate": ["This field is required."]}], "location": "body", "name": "items"}],
    )


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    self.tender_id = response.json["data"]["id"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"status": "cancelled"}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "status",
            "description": [
                "Value must be one of ['draft', 'active.tendering']."
            ]
        }]
    )

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "general"
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
            "endDate": tender["enquiryPeriod"]["endDate"],
        }}},
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
                "description": ["tenderPeriod must be at least 6 full business days long"],
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
        {"data": {"items": [item0]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    item = deepcopy(item0)
    item["classification"] = {"scheme": "ДК021", "id": "44620000-2", "description": "Cartons 2"}
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
        status=200,
    )

    item = deepcopy(item0)
    item["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't change classification")

    item = deepcopy(item0)
    item["additionalClassifications"] = [tender["items"][0]["additionalClassifications"][0] for i in range(3)]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
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

    tender = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"enquiryPeriod": {
            "startDate": calculate_tender_business_date(
                parse_date(new_dateModified), -timedelta(3), None, True
            ).isoformat(),
            "endDate": new_dateModified
        }}},
    )
    result = response.json["data"]
    self.assertEqual(tender["enquiryPeriod"]["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertEqual(tender["enquiryPeriod"]["endDate"], result["enquiryPeriod"]["endDate"])

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def patch_tender_ua(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")
    self.tender_id = tender["id"]
    self.set_enquiry_period_end()

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"value": {"amount": 501, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 2 working days")

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    tender_period_end_date = calculate_tender_business_date(
        get_now(), timedelta(days=7), tender
    ) + timedelta(seconds=10)
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


# TenderUAProcessTest
def one_valid_bid_tender_ua(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering XXX temporary action.
    response = self.set_status(
        "active.tendering", {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
    )
    self.assertIn("auctionPeriod", response.json["data"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, self.test_bids_data[0])

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")


def one_invalid_bid_tender(self):
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
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, self.test_bids_data[0])
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    # get awards
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )

    new_defence_complaints = NEW_DEFENSE_COMPLAINTS_FROM < get_now() < NEW_DEFENSE_COMPLAINTS_TO
    if new_defence_complaints:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}".format(tender_id))
    else:
        # time travel
        tender = self.mongodb.tenders.get(tender_id)
        for i in tender.get("awards", []):
            if i.get("complaintPeriod", None):
                i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
        self.mongodb.tenders.save(tender)
        # set tender status after stand slill period
        response = self.check_chronograph()

    # check status
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


@patch("openprocurement.tender.openuadefense.utils.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.tender_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.belowthreshold.utils.NEW_DEFENSE_COMPLAINTS_FROM", get_now() + timedelta(days=1))
@patch("openprocurement.tender.openuadefense.utils.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.tender_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.belowthreshold.utils.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def one_invalid_bid_tender_before_new(self):
    return one_invalid_bid_tender(self)


@patch("openprocurement.tender.openuadefense.utils.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.tender_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.belowthreshold.utils.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=100))
@patch("openprocurement.tender.openuadefense.utils.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.tender_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
@patch("openprocurement.tender.belowthreshold.utils.NEW_DEFENSE_COMPLAINTS_TO", get_now() - timedelta(days=1))
def one_invalid_bid_tender_after_new(self):
    return one_invalid_bid_tender(self)


@patch("openprocurement.tender.openuadefense.utils.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.tests.tender_blanks.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.belowthreshold.utils.NEW_DEFENSE_COMPLAINTS_FROM", get_now() - timedelta(days=1))
@patch("openprocurement.tender.openuadefense.utils.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.openuadefense.tests.tender_blanks.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
@patch("openprocurement.tender.belowthreshold.utils.NEW_DEFENSE_COMPLAINTS_TO", get_now() + timedelta(days=100))
def one_invalid_bid_tender_new(self):
    return one_invalid_bid_tender(self)


def patch_item_with_zero_quantity(self):
    self.create_tender()
    response = self.app.get("/tenders/{}".format(self.tender_id))
    item = response.json["data"]["items"][0]
    item["quantity"] = 0
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                                   {"data": {"items": [item]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 0)
    item = response.json["data"]["items"][0]
    item["quantity"] = 5
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                                   {"data": {"items": [item]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 5)
    criteria = deepcopy(test_exclusion_criteria)
    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = item["id"]
    add_criteria(self, criteria=criteria)
    item["quantity"] = 0
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                                   {"data": {"items": [item]}})
    self.assertEqual(response.status, "200 OK")
