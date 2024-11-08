from copy import deepcopy
from datetime import timedelta
from unittest import mock

from freezegun import freeze_time

from openprocurement.api.constants import RELEASE_2020_04_19, TZ
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.tests.utils import set_tender_lots
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.requestforproposal.tests.base import (
    test_agreement_rfp_data,
    test_tender_rfp_data,
    test_tender_rfp_organization,
)


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def create_tender_invalid(self):
    request_path = "/tenders"
    # TODO: spent a hour trying find out why this does not work after refactoring
    # response = self.app.post(request_path, "data", status=415)
    # self.assertEqual(response.status, "415 Unsupported Media Type")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             "description": "Content-Type header should be one of ['application/json']",
    #             "location": "header",
    #             "name": "Content-Type",
    #         }
    #     ],
    # )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": 'Expecting value: line 1 column 1 (char 0)', "location": "body", "name": "data"}],
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

    response = self.app.post_json(
        request_path,
        {"data": {"invalid_field": "invalid_value", "procurementMethodType": "requestForProposal"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"value": "invalid_value", "procurementMethodType": "requestForProposal"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Please use a mapping for this field or EstimatedValue instance instead of str."],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethod": "invalid_value", "procurementMethodType": "requestForProposal"}},
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
        {"description": ["This field is required."], "location": "body", "name": "enquiryPeriod"},
        response.json["errors"],
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "value"}, response.json["errors"]
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"enquiryPeriod": {"endDate": "invalid_value"}, "procurementMethodType": "requestForProposal"}},
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
                "procurementMethodType": "requestForProposal",
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

    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2015-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["period should begin after enquiryPeriod"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    now = get_now()
    self.initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    self.initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=14)).isoformat(),
        "endDate": (now + timedelta(days=14)).isoformat(),
    }
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after auctionPeriod"], "location": "body", "name": "awardPeriod"}],
    )
    del self.initial_data["awardPeriod"]
    del self.initial_data["auctionPeriod"]

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

    data = self.initial_data["minimalStep"]
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

    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=201)
    self.initial_data["items"][0]["additionalClassifications"] = data
    self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")

    data = self.initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    cpv_code = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
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
                            "One of additional classifications should be " "one of [ДК003, ДК015, ДК018, specialNorms]."
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
                'description': {'contactPoint': {'telephone': ['wrong telephone format (could be missed +)']}},
                'location': 'body',
                'name': 'procuringEntity',
            }
        ],
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

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "160173000-1"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertIn("Value must be one of", response.json["errors"][0]["description"][0]["classification"]["id"][0])

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertIn("Value must be one of", response.json["errors"][0]["description"][0]["classification"]["id"][0])

    procuringEntity = self.initial_data["procuringEntity"]
    data = self.initial_data["procuringEntity"].copy()
    data["kind"] = "bla"
    self.initial_data["procuringEntity"] = data
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["procuringEntity"] = procuringEntity
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {
                    "kind": [
                        "Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                    ]
                },
            }
        ],
    )
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        request_path,
        {"data": data, "config": {"hasAuction": True, "hasAwardingOrder": False, "valueCurrencyEquality": False}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "valueCurrencyEquality can be False only if hasAuction=False and hasAwardingOrder=False "
                    "and hasValueRestriction=False"
                ],
                "location": "body",
                "name": "valueCurrencyEquality",
            }
        ],
    )
    response = self.app.post_json(
        request_path,
        {"data": data, "config": {"hasAuction": False, "hasAwardingOrder": True, "valueCurrencyEquality": False}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "valueCurrencyEquality can be False only if hasAuction=False and hasAwardingOrder=False "
                    "and hasValueRestriction=False"
                ],
                "location": "body",
                "name": "valueCurrencyEquality",
            }
        ],
    )
    response = self.app.post_json(
        request_path,
        {
            "data": data,
            "config": {
                "hasAuction": True,
                "hasAwardingOrder": True,
                "hasValueRestriction": False,
                "valueCurrencyEquality": False,
            },
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
                "description": [
                    "valueCurrencyEquality can be False only if hasAuction=False and hasAwardingOrder=False "
                    "and hasValueRestriction=False"
                ],
                "location": "body",
                "name": "valueCurrencyEquality",
            }
        ],
    )


def tender_with_main_procurement_category(self):
    data = deepcopy(self.initial_data)

    # test fail creation
    data["mainProcurementCategory"] = "whiskey,tango,foxtrot"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
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
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "goods")

    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update tender in active.enquiries status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "services"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")

    # test update mainProcurementCategory in active.tendering status
    self.set_status("active.tendering")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"mainProcurementCategory": "works"}},
        status=200 if tender["procurementMethodType"] == "requestForProposal" else 403,
    )
    if tender["procurementMethodType"] == "requestForProposal":
        self.assertIn("mainProcurementCategory", response.json["data"])
        self.assertEqual(response.json["data"]["mainProcurementCategory"], "works")
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Can't update tender in current (active.tendering) status",
                }
            ],
        )


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELATED_LOT_REQUIRED_FROM",
    get_now() + timedelta(days=1),
)
def tender_created_before_related_lot_is_required(self):
    data = deepcopy(test_tender_rfp_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    # successfully patch tender without lot
    self.add_sign_doc(self.tender_id, self.tender_token)
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.enquiries"}}, status=200
    )
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELATED_LOT_REQUIRED_FROM",
    get_now() - timedelta(days=1),
)
def tender_created_after_related_lot_is_required(self):
    data = deepcopy(test_tender_rfp_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.add_sign_doc(self.tender_id, self.tender_token)

    # forbid to patch tender without lot
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.enquiries"}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "item.relatedLot", "description": "This field is required"}],
    )

    lots = deepcopy(self.test_lots_data)
    lots.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 15},
        }
    )
    set_tender_lots(data, lots)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.add_sign_doc(self.tender_id, self.tender_token)

    # successfully patch tender with lot
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.enquiries"}}, status=200
    )
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


def check_notice_doc_during_activation(self):
    data = deepcopy(test_tender_rfp_data)
    data["status"] = "draft"
    lots = deepcopy(self.test_lots_data)
    set_tender_lots(data, lots)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.assertNotIn("noticePublicationDate", response.json["data"])

    request_path = f"/tenders/{self.tender_id}?acc_token={self.tender_token}"
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"], "Document with type 'notice' and format pkcs7-signature is required"
    )

    # let's add sign doc
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pdf",
                "documentType": "notice",
            }
        },
    )
    doc_id = response.json["data"]["id"]

    # put document title
    self.app.put_json(
        f"/tenders/{self.tender_id}/documents/{doc_id}?acc_token={self.tender_token}",
        {
            "data": {
                "title": "new.txt",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pdf",
                "documentType": "notice",
            }
        },
    )

    # try to activate tender
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"], "Document with type 'notice' and format pkcs7-signature is required"
    )
    # patch title
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/documents/{doc_id}?acc_token={self.tender_token}",
        {"data": {"title": "sign-2.p7s"}},
    )

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("noticePublicationDate", response.json["data"])
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


def patch_enquiry_tender_periods(self):
    self.create_tender()

    resp = self.app.get(f"/tenders/{self.tender_id}")
    tender = resp.json["data"]

    self.assertEqual(tender["status"], "active.enquiries")
    enq_p = tender["enquiryPeriod"]
    tender_p = tender["tenderPeriod"]

    # check enquiryPeriod:endDate>= enquiryPeriod.startDate + 3 робочі дні
    if get_now() > RELEASE_2020_04_19:
        end_data = calculate_tender_full_date(
            parse_date(enq_p["startDate"], TZ),
            timedelta(days=2),
            tender=tender,
        )
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "enquiryPeriod": {
                        "startDate": enq_p["startDate"],
                        "endDate": end_data.isoformat(),
                    }
                }
            },
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "enquiryPeriod",
                    "description": ["the enquiryPeriod cannot end earlier than 3 calendar days after the start"],
                }
            ],
        )

    # check tenderPeriod:startDate більше ніж enquiryPeriod:endDate
    end_data = calculate_tender_full_date(parse_date(enq_p["startDate"], TZ), timedelta(days=10), tender=tender)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "enquiryPeriod": {
                    "startDate": enq_p["startDate"],
                    "endDate": end_data.isoformat(),
                }
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "tenderPeriod", "description": ["period should begin after enquiryPeriod"]}],
    )

    # tenderPeriod:endDate>= tenderPeriod.startDate + 2 робочі дні
    if get_now() > RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "enquiryPeriod": {
                        "startDate": enq_p["startDate"],
                        "endDate": end_data.isoformat(),
                    },
                    "tenderPeriod": {
                        "startDate": end_data.isoformat(),
                        "endDate": end_data.isoformat(),
                    },
                }
            },
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "tenderPeriod",
                    "description": ["tenderPeriod must be at least 4 full calendar days long"],
                }
            ],
        )

    # all fine
    tender_end = calculate_tender_full_date(end_data, timedelta(days=4), tender=tender)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "status": "active.tendering",
            "data": {
                "enquiryPeriod": {
                    "startDate": enq_p["startDate"],
                    "endDate": end_data.isoformat(),
                },
                "tenderPeriod": {
                    "startDate": end_data.isoformat(),
                    "endDate": tender_end.isoformat(),
                },
            },
        },
        status=200,
    )


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def validate_tender_period(self):
    now = get_now()

    enquiry_start_date = now + timedelta(days=7)
    enquiry_end_date = calculate_tender_full_date(
        enquiry_start_date, timedelta(days=3), tender=self.initial_data, working_days=True
    )

    valid_start_date = enquiry_end_date
    valid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=4), tender=self.initial_data, working_days=True
    ).isoformat()
    invalid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=1), tender=self.initial_data, working_days=True
    ).isoformat()

    enquiry_start_date = enquiry_start_date.isoformat()
    enquiry_end_date = enquiry_end_date.isoformat()
    valid_start_date = valid_start_date.isoformat()

    request_path = "/tenders"
    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {
        "startDate": valid_start_date,
        "endDate": invalid_end_date,
    }
    self.initial_data["enquiryPeriod"] = {
        "startDate": enquiry_start_date,
        "endDate": enquiry_end_date,
    }

    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["tenderPeriod must be at least 4 full calendar days long"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    self.initial_data["tenderPeriod"] = {"startDate": valid_start_date, "endDate": valid_end_date}
    self.initial_data["enquiryPeriod"] = {
        "startDate": enquiry_start_date,
        "endDate": enquiry_end_date,
    }
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    period = tender["tenderPeriod"]
    period["endDate"] = invalid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"tenderPeriod": period}}, status=422
    )

    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["tenderPeriod must be at least 4 full calendar days long"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    period["endDate"] = valid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"tenderPeriod": period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    self.assertEqual(tender["tenderPeriod"]["endDate"], valid_end_date)


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def validate_procurement_method(self):
    request_path = "/tenders"

    data = deepcopy(self.initial_data)
    data["procurementMethod"] = "selective"
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": "procurementMethod should be open",
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
    )

    data["procurementMethod"] = "open"
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procurementMethod"], data["procurementMethod"])

    initial_config = deepcopy(self.initial_config)
    data["procurementMethod"] = "open"
    initial_config["hasPreSelectionAgreement"] = True
    response = self.app.post_json(request_path, {"data": data, "config": initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": "procurementMethod should be selective",
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
    )

    data["procurementMethod"] = "selective"
    response = self.app.post_json(request_path, {"data": data, "config": initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procurementMethod"], data["procurementMethod"])


def tender_inspector(self):
    tender_data = deepcopy(self.initial_data)
    organization = deepcopy(test_tender_rfp_organization)
    del organization["scale"]

    tender_data["inspector"] = organization
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertIn("inspector", response.json["data"])


def tender_funders(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["funders"] = [deepcopy(test_tender_rfp_organization)]
    tender_data["funders"][0]["identifier"]["id"] = "44000"
    tender_data["funders"][0]["identifier"]["scheme"] = "XM-DAC"
    del tender_data["funders"][0]["scale"]
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["id"], "44000")
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["scheme"], "XM-DAC")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    tender_data["funders"].append(deepcopy(test_tender_rfp_organization))
    tender_data["funders"][1]["identifier"]["id"] = "44000"
    tender_data["funders"][1]["identifier"]["scheme"] = "XM-DAC"
    del tender_data["funders"][1]["scale"]
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Funders' identifier should be unique"], "location": "body", "name": "funders"}],
    )

    tender_data["funders"][0]["identifier"]["id"] = "some id"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
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


def patch_tender_active_tendering(self):
    data = deepcopy(self.initial_data)
    data.pop("procurementMethodDetails", None)
    data["tenderPeriod"]["endDate"] = calculate_tender_full_date(
        get_now(),
        timedelta(days=15),
        tender={},
        working_days=True,
    ).isoformat()
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")

    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertNotIn("invalidationDate", tender["enquiryPeriod"])
    self.tender_id = tender["id"]
    self.set_status("active.tendering")

    active_data_patch = dict(
        {
            "guarantee": {"amount": 100500, "currency": "USD"},
            "value": {"amount": 1000.0},
            "title": "New title",
            "description": "New description",
            "documents": [
                {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            ],
        }
    )
    active_data_patch["items"] = deepcopy(self.initial_data["items"])
    active_data_patch["items"][0]["classification"]["id"] = "33600000-6"
    additional_classification_0 = {
        "scheme": "INN",
        "id": "sodium oxybate",
        "description": "папір і картон гофровані, паперова й картонна тара",
    }
    active_data_patch["items"][0]["additionalClassifications"] = [additional_classification_0]

    response = self.app.patch_json(f"/tenders/{self.tender_id}?acc_token={token}", {"data": active_data_patch})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["value"]["amount"], 500)  # as in lot
    self.assertEqual(response.json["data"]["title"], "New title")
    self.assertEqual(response.json["data"]["description"], "New description")
    self.assertEqual(len(response.json["data"]["documents"]), 1)
    self.assertEqual(response.json["data"]["items"][0]["classification"]["id"], "33600000-6")

    # patch tenderPeriod
    end_date = calculate_tender_full_date(get_now(), timedelta(days=16), tender={}, working_days=True)
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={token}", {"data": {"tenderPeriod": {"endDate": end_date.isoformat()}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["tenderPeriod"]["endDate"], tender["tenderPeriod"]["endDate"])
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], end_date.isoformat())
    response = self.app.get(f"/tenders/{self.tender_id}?acc_token={token}")
    tender_updated = response.json["data"]

    with freeze_time((dt_from_iso(tender_updated["tenderPeriod"]["endDate"]) - timedelta(hours=10)).isoformat()):
        end_date = calculate_tender_full_date(get_now(), timedelta(days=1), tender={}, working_days=True)
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={token}",
            {"data": {"tenderPeriod": {"endDate": end_date.isoformat()}}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "data", "description": "tenderPeriod should be extended by 4 working days"}],
        )

    # patch forbidden fields
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={token}",
        {
            "data": {
                "tenderPeriod": {"startDate": get_now().isoformat(), "endDate": end_date.isoformat()},
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "tenderPeriod.startDate",
                "description": "Can't change tenderPeriod.startDate",
            }
        ],
    )

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={token}",
        {"data": {"enquiryPeriod": {}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "enquiryPeriod", "description": "Rogue field"}]
    )

    # check bid invalidation
    bid_data = {
        "tenderers": [test_tender_rfp_organization],
        "lotValues": [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}],
        "subcontractingDetails": "test",
    }
    bid, bid_token = self.create_bid(self.tender_id, bid_data)

    # response = self.app.patch_json(
    #     f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={bid_token}", {"data": {"status": "pending"}}
    # )
    # self.assertEqual(response.status, "200 OK")
    # bid = response.json["data"]
    # self.assertEqual(bid["status"], "pending")

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={token}",
        {"data": {"value": {"amount": 1500.0}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get(f"/tenders/{self.tender_id}?acc_token={token}")
    tender_after = response.json["data"]
    self.assertIn("invalidationDate", tender_after["enquiryPeriod"])
    response = self.app.get(f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={bid_token}")
    self.assertEqual(response.json["data"]["status"], "invalid")


def validate_pre_selection_agreement(self):
    # agreementType mismatch
    agreement = deepcopy(self.initial_agreement_data)
    agreement["agreementType"] = "electronicCatalogue"
    self.mongodb.agreements.save(agreement)
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"status": "active.enquiries"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    print(response.json["errors"][0]["description"])
    self.assertEqual(response.json["errors"][0]["description"], "Agreement type mismatch.")

    # not active agreement
    agreement["agreementType"] = "internationalFinancialInstitutions"
    agreement["status"] = "pending"
    self.mongodb.agreements.save(agreement)
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
        {"data": {"status": "active.enquiries"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["errors"][0]["description"], "Agreement status is not active")


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def validate_enquiry_period(self):
    self.initial_data.pop("procurementMethodDetails", None)

    request_path = "/tenders"
    data = self.initial_data["enquiryPeriod"]
    now = get_now()

    valid_start_date = now + timedelta(days=7)
    valid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=3), tender=self.initial_data
    ).isoformat()
    invalid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=2), tender=self.initial_data
    ).isoformat()
    tender_valid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=8), tender=self.initial_data
    ).isoformat()

    valid_start_date = valid_start_date.isoformat()

    self.initial_data["enquiryPeriod"] = {
        "startDate": valid_start_date,
        "endDate": invalid_end_date,
    }

    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["enquiryPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["the enquiryPeriod cannot end earlier than 3 calendar days after the start"],
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    self.initial_data["enquiryPeriod"] = {
        "startDate": valid_start_date,
        "endDate": valid_end_date,
    }
    self.initial_data["tenderPeriod"] = {
        "endDate": tender_valid_end_date,
    }

    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    period = tender["enquiryPeriod"]
    period["endDate"] = invalid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"enquiryPeriod": period}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["the enquiryPeriod cannot end earlier than 3 calendar days after the start"],
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    period["endDate"] = valid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"enquiryPeriod": period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(tender["enquiryPeriod"]["endDate"], valid_end_date)
