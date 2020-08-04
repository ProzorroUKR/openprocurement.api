# -*- coding: utf-8 -*-
import mock
from datetime import timedelta
from copy import deepcopy

from iso8601 import parse_date
from isodate import duration_isoformat
from mock import patch
from openprocurement.api.constants import (
    CPV_ITEMS_CLASS_FROM,
    SANDBOX_MODE,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
)
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_organization
from uuid import uuid4

from openprocurement.tender.cfaua.constants import MAX_AGREEMENT_PERIOD
from openprocurement.tender.cfaua.models.tender import CloseFrameworkAgreementUA
from openprocurement.tender.cfaua.utils import add_next_awards
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17

# TenderTest
from openprocurement.tender.core.utils import calculate_tender_business_date


def simple_add_tender(self):
    u = CloseFrameworkAgreementUA(self.initial_data)
    u.tenderID = "UA-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.tenderID == fromdb["tenderID"]
    assert u.doc_type == "Tender"
    assert u.procurementMethodType == "closeFrameworkAgreementUA"
    assert fromdb["procurementMethodType"] == "closeFrameworkAgreementUA"

    u.delete_instance(self.db)


# TenderResourceTest


def extract_tender_credentials(self):
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = response.json["data"]["id"]

    self.app.authorization = ("Basic", ("contracting", ""))
    response = self.app.get("/tenders/{}/extract_credentials".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("owner", response.json["data"])
    self.assertIn("tender_token", response.json["data"])
    self.assertIn("id", response.json["data"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/extract_credentials".format(tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )


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
        {"data": {"procurementMethodType": "closeFrameworkAgreementUA", "invalid_field": "invalid_value"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "closeFrameworkAgreementUA", "value": "invalid_value"}},
        status=422,
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
        {"data": {"procurementMethodType": "closeFrameworkAgreementUA", "procurementMethod": "invalid_value"}},
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
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"maxAwardsCount"},
        response.json["errors"],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": "closeFrameworkAgreementUA", "enquiryPeriod": {"endDate": "invalid_value"}}},
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
                "procurementMethodType": "closeFrameworkAgreementUA",
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
    with mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        data = deepcopy(self.initial_data["lots"])
        self.initial_data["lots"][0]["minimalStep"] = {"amount": "1.0"}
        response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
        self.initial_data["lots"] = data
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{u'description':
                  [{u'minimalStep': [u'minimalstep must be between 0.5% and 3% of value (with 2 digits precision).']}],
              u'location': u'body', u'name': u'lots'}
             ]
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

    data = deepcopy(self.initial_data)
    data["maxAwardsCount"] = self.min_bids_number - 1
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Maximal awards number can't be less then minimal bids number"],
                u"location": u"body",
                u"name": u"maxAwardsCount",
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
                u"owner",
                u"procuringEntity",
                u"next_check",
                u"procurementMethod",
                u"awardCriteria",
                u"submissionMethod",
                u"title",
                u"title_en",
                u"date",
                u"maxAwardsCount",
                u"agreementDuration",
                u"lots",
                u"mainProcurementCategory",
                u"milestones",
            ]
        ),
    )
    self.assertNotEqual(data["id"], tender["id"])
    self.assertNotEqual(data["doc_id"], tender["id"])
    self.assertNotEqual(data["tenderID"], tender["tenderID"])
    self.assertEqual(
        set(tender["lots"][0]),
        set([u"status", u"description", u"title", u"minimalStep", u"auctionPeriod", u"value", u"date", u"id"]),
    )


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")
    self.initial_lots = tender["lots"]

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

    # response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.auction'}})
    # self.assertEqual(response.status, '200 OK')

    # response = self.app.get('/tenders/{}'.format(tender['id']))
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('auctionUrl', response.json['data'])
    initial_bids = deepcopy(self.initial_bids)
    self.convert_bids_for_tender_with_lots(initial_bids, self.initial_lots)
    for bid in initial_bids:
        response = self.app.post_json("/tenders/{}/bids".format(tender["id"]), {"data": bid})

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")

    with mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        lots = deepcopy(self.initial_lots)
        lots[0]["minimalStep"]["amount"] = 123
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
            {"data": {"lots": lots}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{u'description':
                  [{u'minimalStep': [u'minimalstep must be between 0.5% and 3% of value (with 2 digits precision).']}],
              u'location': u'body', u'name': u'lots'}
             ],
        )


def patch_tender_period(self):
    data = deepcopy(self.initial_data)
    data["lots"] = self.initial_lots
    if SANDBOX_MODE:
        data["procurementMethodDetails"] = "quick, accelerator=1440"
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"agreementDuration": "P0Y0M1DT1M0,2S"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["agreementDuration"], "P1DT1M0.2S")

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


def tender_contract_period(self):
    self.app.authorization = ("Basic", ("broker", ""))
    data = deepcopy(self.initial_data)
    data["lots"] = self.initial_lots
    lot_id = uuid4().hex
    data["lots"][0]["id"] = lot_id
    for item in data["items"]:
        item["relatedLot"] = lot_id
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.app.authorization = ("Basic", ("token", ""))
    # active.tendering
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, owner_token),
        {"data": {"contractPeriod": {"endDate": "2018-08-09"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # patch shouldn't affect changes
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("contractPeriod", response.json["data"])

    self.set_status("active.awarded")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("contractPeriod", response.json["data"])
    self.assertNotIn("endDate", response.json["data"]["contractPeriod"])

    self.set_status("complete")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("contractPeriod", response.json["data"])
    self.assertIn("endDate", response.json["data"]["contractPeriod"])


def patch_unitprice_with_features(self):
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
            "enum": [
                {"value": 0.05, "title": u"До 90 днів"},
                {"value": 0.01, "title": u"Більше 90 днів"},
                {"value": 0, "title": u"Більше 90 днів"},
            ],
        },
        {
            "code": "OCDS-123454-POSTPONEMENN",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "description": u"Термін відстрочки платежу",
            "enum": [
                {"value": 0.05, "title": u"До 90 днів"},
                {"value": 0.01, "title": u"Більше 90 днів"},
                {"value": 0, "title": u"Більше 90 днів"},
            ],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    initial_bids = deepcopy(self.initial_bids)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    for bid_data in initial_bids:
        bid_data["parameters"] = [
            {"code": "OCDS-123454-POSTPONEMENT", "value": 0},
            {"code": "OCDS-123454-POSTPONEMENN", "value": 0.05},
        ]

        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bid_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    self.set_status("active.qualification.stand-still", "end")

    self.check_chronograph()
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))

    contracts = response.json["data"]["agreements"][-1]["contracts"]
    agreement_id = response.json["data"]["agreements"][-1]["id"]

    for contract in contracts:
        unit_prices = contract["unitPrices"]
        for unit_price in unit_prices:
            unit_price["value"]["amount"] = 60
        response = self.app.patch_json(
            "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
                self.tender_id, agreement_id, contract["id"], owner_token
            ),
            {"data": {"unitPrices": unit_prices}},
        )
        self.assertEqual(response.status, "200 OK")


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

    initial_bids = deepcopy(self.initial_bids)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = initial_bids[0]
    bid_data["parameters"] = [{"code": "OCDS-123454-POSTPONEMENT", "value": 0.1}]
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

    # switch to active.qualification
    self.set_status("active.tendering", "end")
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
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    initial_bids = deepcopy(self.initial_bids)

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": initial_bids[0]})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(tender_id, self.initial_lots[0]["id"], owner_token), status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {u"description": [u"Please provide at least 1 item."], u"location": u"body", u"name": u"lots"},
            {
                u"description": [{u"relatedLot": [u"relatedLot should be one of lots"]}],
                u"location": u"body",
                u"name": u"items",
            },
        ],
    )

    # switch to active.qualification
    self.set_status("active.tendering", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


# TenderProcessTest


def one_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])

    data = deepcopy(self.initial_data)

    # create tender
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = self.tender_id = response.json["data"]["id"]
    # create bid
    bidder_data = deepcopy(test_organization)
    initial_bids = deepcopy(self.initial_bids)
    initial_bids[0]["tenderers"] = bidder_data
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": initial_bids[1]})
    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
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
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # create bid
    bidder_data = deepcopy(test_organization)
    initial_bids = deepcopy(self.initial_bids)

    self.app.authorization = ("Basic", ("broker", ""))
    initial_bids[0]["tenderers"] = [bidder_data]
    for x in range(self.min_bids_number):
        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": initial_bids[0]})

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.assertEqual(len(qualifications), self.min_bids_number)
    # disqualify all bids
    self.app.authorization = ("Basic", ("broker", ""))
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualification["id"], owner_token),
            {"data": {"status": "unsuccessful"}},
        )
        self.assertEqual(response.status, "200 OK")
    # switch to next status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    assert_data = {u"id", u"status", u"tenderers", u"selfQualified"}
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data.add(u"selfEligible")
    for bid in response.json["data"]["bids"]:
        self.assertEqual(bid["status"], "unsuccessful")
        self.assertEqual(set(bid.keys()), assert_data)


def one_qualificated_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    self.initial_lots = response.json["data"]["lots"]
    # create bids
    bidder_data = deepcopy(test_organization)
    initial_bids = deepcopy(self.initial_bids)
    self.app.authorization = ("Basic", ("broker", ""))

    initial_bids[0]["tenderers"] = [bidder_data]
    for i in range(self.min_bids_number):
        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": initial_bids[0]})

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.assertEqual(len(qualifications), self.min_bids_number)
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
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[i]["id"], tender_owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
    self.assertEqual(response.status, "200 OK")
    # bid should be activated
    response = self.app.get("/tenders/{}/bids/{}".format(tender_id, qualifications[0]["bidID"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # invalidate second qualification/bid
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            tender_id, qualifications[self.min_bids_number - 1]["id"], tender_owner_token
        ),
        {"data": {"status": "unsuccessful"}},
    )

    # bid should be cancelled
    response = self.app.get("/tenders/{}/bids/{}".format(tender_id, qualifications[self.min_bids_number - 1]["bidID"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotIn("value", response.json["data"])
    # switch to next status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, tender_owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    # tender should switch to "unsuccessful"
    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    # ensure that tender has been switched to "unsuccessful"
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def multiple_bidders_tender(self):
    # create tender
    self.app.authorization = ("Basic", ("broker", ""))
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_owner_token = response.json["access"]["token"]
    # create bids
    bidder_data = deepcopy(test_organization)
    self.app.authorization = ("Basic", ("broker", ""))

    bids_data = deepcopy(self.initial_bids)
    bids_data[0]["tenderers"] = [bidder_data]
    for i in range(self.min_bids_number):
        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bids_data[0]})

    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bids_data[0]})
    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    self.assertEqual(len(qualifications), self.min_bids_number + 1)
    # approve first two bids qualification/bid
    self.app.authorization = ("Basic", ("broker", ""))
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(tender_id, qualifications[i]["id"], tender_owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # cancel qualification for second bid
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            tender_id, qualifications[self.min_bids_number - 1]["id"], tender_owner_token
        ),
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
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            tender_id, qualifications[self.min_bids_number]["id"], tender_owner_token
        ),
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
    # 'active.auction' status can't be set with chronograpth tick
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    # time traver
    self.set_status("active.pre-qualification.stand-still", "end")
    # change tender state
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")

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
    self.assertEqual(response.status, "200 OK")
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, tender_owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, tender_owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, tender_owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award2_id, tender_owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]

    # XXX rewrite following part with less of magic actions
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("active.awarded", "end")
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, tender_owner_token),
        {"data": {"status": "active"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def lost_contract_for_active_award(self):
    # create tender
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # create bids
    bids_data = deepcopy(self.initial_bids)
    for i in range(self.min_bids_number):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bids_data[0]})

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
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
    # lost agreement
    tender = self.db.get(tender_id)
    tender["agreements"] = None
    self.db.save(tender)
    # check tender
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertNotIn("agreements", response.json["data"])
    self.assertIn("next_check", response.json["data"])
    # create lost agreement
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"id": tender_id}})
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("agreements", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def patch_tender_active_qualification_2_active_qualification_stand_still(self):
    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")

    awards = response.json["data"]
    for award in awards:
        self.assertEqual(award["status"], "pending")

    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, awards[0]["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )

    # try to switch not all awards qualified
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        u"Can't switch to 'active.qualification.stand-still' while not all awards are qualified",
    )

    for award in awards[1:]:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")

    # check award.complaintPeriod.endDate
    tender = response.json["data"]
    for award in tender["awards"]:
        self.assertEqual(award["complaintPeriod"]["endDate"], tender["awardPeriod"]["endDate"])


def switch_tender_to_active_awarded(self):
    """ Test for switch tender from active.qualification.stand-still to active.awarded """

    status = "active.qualification.stand-still"
    self.set_status(status)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], status)

    # Try switch with role 'broker'
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )

    # Try switch before awardPeriod complete
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], status)
    self.assertGreater(response.json["data"]["awardPeriod"]["endDate"], get_now().isoformat())

    # Switch after awardPeriod complete
    # Use timeshift
    with patch("openprocurement.tender.cfaua.utils.get_now") as mocked_time:
        mocked_time.return_value = parse_date(response.json["data"]["awardPeriod"]["endDate"])
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contractPeriod", response.json["data"])


def patch_max_awards(self):
    min_awards_number = self.min_bids_number

    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.patch_json(
        "/tenders/{}".format(self.tender_id), {"data": {"maxAwardsCount": min_awards_number - 1}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Maximal awards number can't be less then minimal bids number"],
                u"location": u"body",
                u"name": u"maxAwardsCount",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"maxAwardsCount": min_awards_number}},
    )
    tender = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(tender["maxAwardsCount"], min_awards_number)

    self.set_status("active.pre-qualification")
    # should not change max awards number in active.pre-qualification
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"maxAwardsCount": min_awards_number + 1}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(tender["maxAwardsCount"], min_awards_number + 1)


def _awards_to_bids_number(self, max_awards_number, bids_number, expected_awards_number):

    initial_data = deepcopy(self.initial_data)
    initial_data["maxAwardsCount"] = max_awards_number

    response = self.app.post_json("/tenders", {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.initial_lots = response.json["data"]["lots"]
    # create bids
    initial_bids = deepcopy(self.initial_bids)
    initial_bids[0]["tenderers"] = [test_organization]
    for _ in range(bids_number):
        response = self.app.post_json(
            "/tenders/{}/bids?acc_token={}".format(self.tender_id, self.tender_token), {"data": initial_bids[0]}
        )
    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    # list qualifications
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    # approve qualification
    for qualification in qualifications:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.set_status("active.auction")
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": {"bids": auction_bids_data}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), expected_awards_number)


def awards_to_bids_number(self):
    self.app.authorization = ("Basic", ("broker", ""))
    _awards_to_bids_number(self, max_awards_number=3, bids_number=3, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=3, bids_number=4, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=3, bids_number=5, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=4, bids_number=3, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=4, bids_number=4, expected_awards_number=4)
    _awards_to_bids_number(self, max_awards_number=4, bids_number=5, expected_awards_number=4)
    _awards_to_bids_number(self, max_awards_number=5, bids_number=3, expected_awards_number=3)
    _awards_to_bids_number(self, max_awards_number=5, bids_number=4, expected_awards_number=4)
    _awards_to_bids_number(self, max_awards_number=5, bids_number=5, expected_awards_number=5)


def active_qualification_to_act_pre_qualification_st(self):
    self.set_status("active.qualification", "end")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.auction"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Can't update tender status", u"location": u"body", u"name": u"data"}],
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Can't update tender status", u"location": u"body", u"name": u"data"}],
    )


def active_pre_qualification_to_act_qualification_st(self):
    self.set_status("active.pre-qualification", "end")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Can't update tender status", u"location": u"body", u"name": u"data"}],
    )


def agreement_duration_period(self):
    initial_data = deepcopy(self.initial_data)
    initial_data["agreementDuration"] = "P5Y"
    response = self.app.post_json("/tenders", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    u"Agreement duration period is greater than {}".format(duration_isoformat(MAX_AGREEMENT_PERIOD))
                ],
                u"location": u"body",
                u"name": u"agreementDuration",
            }
        ],
    )
    initial_data["agreementDuration"] = "P3Y12M1D"
    response = self.app.post_json("/tenders", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    u"Agreement duration period is greater than {}".format(duration_isoformat(MAX_AGREEMENT_PERIOD))
                ],
                u"location": u"body",
                u"name": u"agreementDuration",
            }
        ],
    )
    initial_data["agreementDuration"] = "P4YT1H"
    response = self.app.post_json("/tenders", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    u"Agreement duration period is greater than {}".format(duration_isoformat(MAX_AGREEMENT_PERIOD))
                ],
                u"location": u"body",
                u"name": u"agreementDuration",
            }
        ],
    )
    initial_data["agreementDuration"] = "P4Y"
    response = self.app.post_json("/tenders", {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


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
                u"description": [{u"enum": [{u"value": [u"Value should be less than 0.3."]}]}],
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
                "description": ["Value must be one of ['goods', 'services']."],
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
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "goods"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "goods")
