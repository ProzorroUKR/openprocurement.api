from copy import deepcopy
from unittest import mock

from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.tests.base import test_tender_arma_bids
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
)
from openprocurement.tender.core.tests.utils import change_auth, set_bid_items

# TenderBidResourceTest


def create_tender_biddder_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids",
        {"data": {"tenderers": self.test_bids_data[0]["tenderers"], "value": {"amount": 500}}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    request_path = "/tenders/{}/bids".format(self.tender_id)
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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": "invalid_value"}]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "identifier": ["Please use a mapping for this field or Identifier instance instead of str."]
                },
                "location": "body",
                "name": "tenderers",
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": {"tenderers": [{"identifier": {}}]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    assert_data = [
        {
            "description": [
                {
                    "contactPoint": ["This field is required."],
                    "identifier": {"scheme": ["This field is required."], "id": ["This field is required."]},
                    "name": ["This field is required."],
                    "address": ["This field is required."],
                    "scale": ["This field is required."],
                }
            ],
            "location": "body",
            "name": "tenderers",
        },
        {"description": ["This field is required."], "location": "body", "name": "selfQualified"},
    ]
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data.insert(
            0,
            {"description": ["This field is required."], "location": "body", "name": "selfEligible"},
        )

    self.assertEqual(response.json["errors"], assert_data)

    response = self.app.post_json(
        request_path,
        {"data": {"selfEligible": False, "tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}]}},
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
                    {
                        "contactPoint": ["This field is required."],
                        "identifier": {
                            "scheme": ["This field is required."],
                            "id": ["This field is required."],
                            "uri": ["Not a well formed URL."],
                        },
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "tenderers",
            },
            {"description": ["This field is required."], "location": "body", "name": "selfQualified"},
            {"description": ["Value must be one of [True]."], "location": "body", "name": "selfEligible"},
        ],
    )

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["lotValues"]
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "lotValues"}],
    )

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500, "valueAddedTaxIncluded": False}
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {
                        "value": [
                            "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                        ]
                    }
                ],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    bid_data["lotValues"][0]["value"] = {"amount": 500, "currency": "USD"}
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )


def create_tender_bidder(self):
    bid_data = deepcopy(test_tender_arma_bids[0])
    lot_id = self.initial_lots[0]["id"]
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}],
            "value": None,
            "parameters": None,
            "documents": None,
            "financialDocuments": None,
            "eligibilityDocuments": None,
            "qualificationDocuments": None,
        }
    )
    set_bid_items(self, bid_data)
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], self.test_bids_data[0]["tenderers"][0]["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    for status in ("active", "unsuccessful", "deleted", "invalid"):
        bid_data["status"] = status
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("brokerfdd", ""))
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = auth

    self.set_status("complete")

    del bid_data["status"]
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def patch_tender_bidder(self):
    bid_data = deepcopy(test_tender_arma_bids[0])
    lot_id = self.initial_lots[0]["id"]
    bid_data.pop("value", None)
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}],
        }
    )
    bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")

    tenderer = deepcopy(test_tender_below_supplier)
    tenderer["name"] = "Державне управління управлінням справами"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bid["id"], bid_token)
    doc_id = response.json["data"]["documents"][-1]["id"]
    self.assertNotEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {
            "data": {
                "lotValues": [{"value": {"amount": 600}, "relatedLot": lot_id}],
                "tenderers": self.test_bids_data[0]["tenderers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bid["id"], bid_token, doc_id)
    self.assertNotEqual(response.json["data"]["date"], bid["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {
            "data": {
                "lotValues": [{"value": {"amount": 440}, "relatedLot": lot_id}],
                "value": None,
                "parameters": None,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bid["id"], bid_token, doc_id)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 440)

    response = self.app.patch_json(
        "/tenders/{}/bids/some_id?acc_token={}".format(self.tender_id, bid_token),
        {"data": {"lotValues": [{"value": {"amount": 440}, "relatedLot": lot_id}]}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.patch_json("/tenders/some_id/bids/some_id", {"data": {"value": {"amount": 400}}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    for status in ("invalid", "active", "unsuccessful", "deleted", "draft"):
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update bid to ({}) status".format(status))

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 440)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": [{"value": {"amount": 440}, "relatedLot": lot_id}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


def patch_tender_draft_bidder(self):
    lot_id = self.initial_lots[0]["id"]
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "lotValues": [{"value": {"amount": 500}, "relatedLot": lot_id}],
            "status": "draft",
        }
    )
    set_bid_items(self, bid_data)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]
    lot_values = bid["lotValues"]
    lot_values[0]["value"]["amount"] = 499

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "draft", "lotValues": lot_values}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    lot_values[0]["value"]["amount"] = 498
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "draft", "lotValues": lot_values}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def get_tender_bidder(self):
    bid_data = deepcopy(test_tender_arma_bids[0])
    bid_data.pop("value", None)
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "lotValues": self.test_bids_data[0]["lotValues"],
        }
    )
    for _ in range(self.min_bids_number - 1):
        bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")

    self.create_bid(self.tender_id, bid_data, "pending")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid in current (active.tendering) tender status"
    )

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], bid)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    with change_auth(self.app, ("Basic", ("anon", ""))):
        response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(
            set(b.keys()),
            {"id", "status", "tenderers", "lotValues", "items"},
        )
        for lot_value in b["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    with change_auth(self.app, ("Basic", ("anon", ""))):
        response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(
            set(b.keys()),
            {"id", "status", "tenderers", "lotValues", "items"},
        )
        for lot_value in b["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    with change_auth(self.app, ("Basic", ("anon", ""))):
        response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(
            set(b.keys()),
            {"id", "status", "tenderers", "lotValues", "items"},
        )
        for lot_value in b["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )

    # switch to qualification
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        response = self.app.post_json(
            "/tenders/{}/auction".format(self.tender_id),
            {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}},
        )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    with change_auth(self.app, ("Basic", ("anon", ""))):
        response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    assert_keys = ["date", "status", "id", "lotValues", "tenderers", "selfQualified", "submissionDate", "items"]
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_keys.append("selfEligible")
    for b in response.json["data"]:
        self.assertEqual(set(b.keys()), set(assert_keys))

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_keys),
    )

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(set(b.keys()), set(assert_keys))

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_keys),
    )

    self.set_status("complete")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), self.min_bids_number)
    for b in response.json["data"]:
        self.assertEqual(set(b.keys()), set(assert_keys))

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_keys),
    )


def create_tender_bid_no_scale_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "lotValues": [
                {
                    "relatedLot": self.tender_lots[0]["id"],
                    "value": {
                        "amount": 500,
                    },
                }
            ],
            "tenderers": [{key: value for key, value in self.author_data.items() if key != "scale"}],
        }
    )
    response = self.app.post_json(request_path, {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"scale": ["This field is required."]}], "location": "body", "name": "tenderers"}],
    )


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def delete_tender_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], bid)

    revisions = self.mongodb.tenders.get(self.tender_id).get("revisions")
    self.assertTrue(any(i for i in revisions[-1]["changes"] if i["op"] == "add" and i["path"] == "/bids"))

    response = self.app.delete("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.delete("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    # create new bid
    bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")
    # update tender. Bids will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"title": "New one"}}
    )
    self.assertEqual(response.status, "200 OK")

    # check bid 'invalid' status
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid")

    # try to delete 'invalid' bid
    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    for i in range(self.min_bids_number):
        bid_data["lotValues"][0]["value"] = {"amount": 500 - i}
        self.create_bid(self.tender_id, bid_data, "pending")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.set_status("complete")

    # finished tender does not have deleted bid
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])


def get_tender_tenderers(self):
    bid_data = deepcopy(test_tender_arma_bids[0])
    bid_data.pop("value", None)
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "lotValues": self.test_bids_data[0]["lotValues"],
        }
    )
    bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bids in current (active.tendering) tender status"
    )
    for _ in range(self.min_bids_number - 1):
        self.create_bid(self.tender_id, bid_data, "pending")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    bid_data = response.json["data"][0]
    self.assertEqual(bid_data["id"], bid["id"])
    self.assertEqual(bid_data["status"], "active")
    self.assertTrue("lotValues" in bid_data)
    self.assertTrue("tenderers" in bid_data)
    self.assertTrue("date" in bid_data)

    response = self.app.get("/tenders/some_id/bids", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def bid_Administrator_change(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    set_bid_items(self, bid_data)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    bid_data["tenderers"][0]["identifier"]["id"] = "00000000"
    bid_data["lotValues"] = bid["lotValues"]
    bid_data["lotValues"][0]["value"] = {"amount": 400}
    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["id"], "00000000")


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def bids_invalidation_on_tender_change(self):
    bids_access = {}

    # submit bids
    for data in self.test_bids_data:
        bid, bid_token = self.create_bid(self.tender_id, data, "pending")
        bids_access[bid["id"]] = bid_token

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    # update tender and bids will be invalidated by this request
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"description": "new description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "new description")

    # check bids status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
    # try to add documents to bid
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, bid_id, doc_resource, token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        # self.assertEqual(response.json["errors"][0]["description"], "Can't add document at 'invalid' bid status")

    # check that tender status change does not invalidate bids
    # submit valid bid
    data = deepcopy(self.test_bids_data[0])
    data["lotValues"][0]["value"]["amount"] = 499
    bid, valid_bid_token = self.create_bid(self.tender_id, data, "pending")
    valid_bid_id = bid["id"]
    valid_bid_date = bid["date"]

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"]["amount"] = 441

    for i in range(1, self.min_bids_number):
        bid_data.update({"tenderers": self.test_bids_data[i]["tenderers"]})
        bid, bid_token = self.create_bid(self.tender_id, bid_data, "pending")

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))

    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, valid_bid_id, valid_bid_token))
    self.assertEqual(response.json["data"]["status"], "active")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # tender should display all bids
    self.assertEqual(len(response.json["data"]["bids"]), self.min_bids_number * 2)
    self.assertEqual(response.json["data"]["bids"][self.min_bids_number]["date"], valid_bid_date)
    # invalidated bids should show only 'id' and 'status' fields
    for bid in response.json["data"]["bids"]:
        if bid["status"] == "invalid":
            self.assertTrue("id" in bid)
            self.assertTrue("lotValues" in bid)
            self.assertFalse("value" in bid["lotValues"][0])
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)

    # invalidated bids stay invalidated
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")
        # invalidated bids displays only 'id' and 'status' fields
        self.assertTrue("lotValues" in response.json["data"])
        self.assertFalse("value" in response.json["data"]["lotValues"][0])
        self.assertFalse("tenderers" in response.json["data"])
        self.assertFalse("date" in response.json["data"])

    # and valid bid is not invalidated
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, valid_bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    # and displays all his data
    self.assertTrue("lotValues" in response.json["data"])
    self.assertTrue("value" in response.json["data"]["lotValues"][0])
    self.assertTrue("tenderers" in response.json["data"])
    self.assertTrue("date" in response.json["data"])

    # check bids availability on finished tender
    self.set_status("complete")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]["bids"]), self.min_bids_number * 2)
    for bid in response.json["data"]["bids"]:
        if bid["id"] in bids_access:  # previously invalidated bids
            self.assertEqual(bid["status"], "invalid")
            self.assertTrue("lotValues" in bid)
            self.assertFalse("value" in bid["lotValues"][0])
            self.assertFalse("tenderers" in bid)
            self.assertFalse("date" in bid)
        else:  # valid bid
            self.assertEqual(bid["status"], "active")
            self.assertTrue("lotValues" in bid)
            self.assertTrue("value" in bid["lotValues"][0])
            self.assertTrue("tenderers" in bid)
            self.assertTrue("date" in bid)


def bids_activation_on_tender_documents(self):
    bids_access = {}

    # submit bids
    for data in deepcopy(self.test_bids_data):
        data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
        bid, bid_token = self.create_bid(self.tender_id, data, "pending")
        bids_access[bid["id"]] = bid_token

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    for bid_id, token in bids_access.items():
        response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "invalid")

    # activate bids
    for bid_id, token in bids_access.items():
        response = self.app.patch_json(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token), {"data": {"status": "pending"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")


# TenderBidDocumentResourceTest


def not_found(self):
    auth = self.app.authorization
    document = {
        "title": "укр.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }
    for doc_resource in ["financial_documents", "eligibility_documents", "qualification_documents"]:
        self.app.authorization = auth
        response = self.app.post_json(
            "/tenders/some_id/bids/some_id/{}?acc_token={}".format(doc_resource, self.bid_token),
            {"data": document},
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
        )

        response = self.app.post_json(
            "/tenders/{}/bids/some_id/{}?acc_token={}".format(self.tender_id, doc_resource, self.bid_token),
            {"data": document},
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

        response = self.app.get(
            "/tenders/some_id/bids/some_id/{}?acc_token={}".format(doc_resource, self.bid_token), status=404
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
        )

        response = self.app.get(
            "/tenders/{}/bids/some_id/{}?acc_token={}".format(self.tender_id, doc_resource, self.bid_token), status=404
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

        response = self.app.get(
            "/tenders/some_id/bids/some_id/{}/some_id?acc_token={}".format(doc_resource, self.bid_token), status=404
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
        )

        response = self.app.get(
            "/tenders/{}/bids/some_id/{}/some_id?acc_token={}".format(self.tender_id, doc_resource, self.bid_token),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/some_id?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, self.bid_token
            ),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
        )

        response = self.app.put_json(
            "/tenders/some_id/bids/some_id/{}/some_id?acc_token={}".format(doc_resource, self.bid_token),
            {"data": document},
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
        )

        response = self.app.put_json(
            "/tenders/{}/bids/some_id/{}/some_id?acc_token={}".format(self.tender_id, doc_resource, self.bid_token),
            {"data": document},
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/some_id?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, self.bid_token
            ),
            {"data": document},
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
        )


def get_tender_bidder_document(self):
    doc_id_by_type = {}

    def document_is_unaccessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker2", ""))
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def document_is_unaccessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, resource, doc_id, self.tender_token
            ),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def all_documents_are_accessible_for_bid_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        for resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.bid_token)
            )
            self.assertEqual(response.status, "200 OK")
            doc1 = response.json["data"][0]
            doc2 = response.json["data"][1]
            self.assertEqual(doc1["title"], "name_{}.doc".format(resource[:-1]))
            self.assertEqual(doc2["title"], "name_{}_private.doc".format(resource[:-1]))
            self.assertEqual(doc1["confidentiality"], "public")
            self.assertEqual(doc2["confidentiality"], "buyerOnly")
            self.assertIn("url", doc1)
            self.assertIn("url", doc2)
            doc_id = doc_id_by_type[resource]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            doc = response.json["data"]
            doc.pop("previousVersions", None)
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource + "private"]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            doc = response.json["data"]
            doc.pop("previousVersions", None)
            self.assertEqual(doc, doc2)
        self.app.authorization = orig_auth

    def documents_are_accessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        token = self.tender_token
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, token)
        )
        self.assertEqual(response.status, "200 OK")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertIn("url", response.json["data"])
        self.assertEqual(response.status, "200 OK")
        doc_id = doc_id_by_type[resource + "private"]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("url", response.json["data"])
        self.app.authorization = orig_auth

    def public_documents_are_accessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker2", ""))

        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource))
        self.assertEqual(response.status, "200 OK")
        self.assertIn(doc_id_by_type[resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id_by_type[resource]["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}.doc".format(resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], "public")
        self.assertEqual(response.json["data"]["format"], "application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid_id, resource, doc_id_by_type[resource + "private"]["id"]
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["confidentiality"], "buyerOnly")
        self.assertNotIn("url", response.json["data"])

        self.app.authorization = orig_auth

    def all_public_documents_are_accessible_for_others():
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            public_documents_are_accessible_for_others(doc_resource)

    # active.tendering
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        # upload private document
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}_private.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}_private.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    all_documents_are_accessible_for_bid_owner(doc_resource)
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    with change_auth(self.app, ("Basic", ("anon", ""))):
        response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for bid in response.json["data"]:
        for lot_value in bid["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )

    for doc_resource in ["documents", "eligibility_documents"]:
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, doc_resource))
        self.assertEqual(response.status, "200 OK")
        self.assertIn("url", response.json["data"][0])
        self.assertIn(doc_id_by_type[doc_resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

    for doc_resource in ["documents", "eligibility_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], "public")
        self.assertEqual(response.json["data"]["format"], "application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        doc_id = doc_id_by_type[doc_resource + "private"]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}_private.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], "buyerOnly")
        self.assertEqual(response.json["data"]["format"], "application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for bid in response.json["data"]:
        for lot_value in bid["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], "public")
    self.assertEqual(response.json["data"]["format"], "application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for bid in response.json["data"]:
        for lot_value in bid["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], "public")
    self.assertEqual(response.json["data"]["format"], "application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    assert_data = [
        "date",
        "status",
        "id",
        "lotValues",
        "tenderers",
        "documents",
        "eligibilityDocuments",
        "qualificationDocuments",
        "financialDocuments",
        "selfQualified",
        "submissionDate",
        "items",
    ]
    assert_data_less = ["date", "status", "id", "lotValues", "tenderers", "selfQualified", "submissionDate", "items"]
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data.append("selfEligible")
        assert_data_less.append("selfEligible")
    self.assertEqual(
        set(response.json["data"][0].keys()),
        set(assert_data),
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        set(assert_data_less),
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_data),
    )

    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        set(assert_data),
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        set(assert_data_less),
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_data),
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    self.set_status("complete")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        set(assert_data),
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        set(assert_data_less),
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_data),
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()


def create_tender_bidder_document(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]

        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id_by_type[doc_resource]["id"], response.json["data"][0]["id"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"][0]["title"])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}?all=true&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id_by_type[doc_resource]["id"], response.json["data"][0]["id"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"][0]["title"])

        doc_id = doc_id_by_type[doc_resource]["id"]
        key = doc_id_by_type[doc_resource]["key"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}".format(self.tender_id, self.bid_id, doc_resource, doc_id, key),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token
            )
        )
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertIn("Expires=", response.location)

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    auth = self.app.authorization
    response = self.check_chronograph()
    self.app.authorization = auth

    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't add document in current (active.pre-qualification) tender status",
        )

    # list qualifications
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't add document in current (active.pre-qualification.stand-still) tender status",
        )

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't add document in current (active.auction) tender status"
        )

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't add document because award of bid is not in one of statuses ('active',)",
        )

    self.set_status("complete")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
        )


def put_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": self.get_doc_id_from_url(response.json["data"]["url"])}

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id_by_type2[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": self.get_doc_id_from_url(response.json["data"]["url"]),
        }

        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token
            )
        )
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertIn("Expires=", response.location)

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)
    self.activate_bid(self.tender_id, self.bid2_id, self.bid2_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    auth = self.app.authorization
    response = self.check_chronograph()
    self.app.authorization = auth

    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document in current (active.pre-qualification) tender status",
        )

    # list qualifications
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document in current (active.pre-qualification.stand-still) tender status",
        )

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update document in current (active.auction) tender status"
        )

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid2_id, doc_resource, doc_id_by_type2[doc_resource]["id"], self.bid2_token
            ),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in one of statuses ('active',)",
        )

    self.set_status("complete")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": document},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
        )


def patch_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id_by_type2[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": self.get_doc_id_from_url(response.json["data"]["url"]),
        }

        # upload private document
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}_private.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}_private.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid2_id, doc_resource, self.bid2_token),
            {
                "data": {
                    "title": "name_{}_private.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}_private.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type2[doc_resource + "private"] = {"id": doc_id, "key": key}
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid2_id, doc_resource, doc_id, self.bid2_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {"data": {"documentOf": "lot"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": ["This field is required."], "location": "body", "name": "relatedItem"}],
        )

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {"data": {"documentOf": "lot", "relatedItem": "0" * 32}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{"description": ["relatedItem should be one of lots"], "location": "body", "name": "relatedItem"}],
        )

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {"data": {"description": "document description", "language": "en"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual("document description", response.json["data"]["description"])
        self.assertEqual("en", response.json["data"]["language"])

        # test confidentiality change
        doc_id = doc_id_by_type[doc_resource + "private"]["id"]
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {"data": {"confidentiality": "public", "confidentialityRationale": ""}},
        )
        self.assertEqual(response.status, "200 OK")
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)
    self.activate_bid(self.tender_id, self.bid2_id, self.bid2_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"status": "active.tendering"})
    auth = self.app.authorization
    response = self.check_chronograph()
    self.app.authorization = auth

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document in current (active.pre-qualification) tender status",
        )

    # list qualifications
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document in current (active.pre-qualification.stand-still) tender status",
        )
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id,
                self.bid_id,
                doc_resource,
                doc_id_by_type[doc_resource + "private"]["id"],
                self.bid_token,
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document in current (active.pre-qualification.stand-still) tender status",
        )

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update document in current (active.auction) tender status"
        )
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id,
                self.bid_id,
                doc_resource,
                doc_id_by_type[doc_resource + "private"]["id"],
                self.bid_token,
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update document in current (active.auction) tender status"
        )

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": {"description": "document description2"}},
            status=403,
        )
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in one of statuses ('active',)",
        )

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid2_id, doc_resource, doc_id_by_type2[doc_resource]["id"], self.bid2_token
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in one of statuses ('active',)",
        )
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id,
                self.bid2_id,
                doc_resource,
                doc_id_by_type2[doc_resource + "private"]["id"],
                self.bid2_token,
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in one of statuses ('active',)",
        )

    self.set_status("complete")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]["id"], self.bid_token
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
        )
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id,
                self.bid_id,
                doc_resource,
                doc_id_by_type[doc_resource + "private"]["id"],
                self.bid_token,
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
        )


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def patch_and_put_document_into_invalid_bid(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"description": "new description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "new description")

    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")


def download_tender_bidder_document(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        private_doc_id_by_type[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": key,
        }

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {
            "id": response.json["data"]["id"],
            "key": key,
        }

        for container in private_doc_id_by_type, doc_id_by_type:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    container[doc_resource]["id"],
                    self.bid_token,
                    container[doc_resource]["key"],
                )
            )

            self.assertEqual(response.status, "302 Moved Temporarily")
            self.assertIn("http://localhost/get/", response.location)
            self.assertIn("Signature=", response.location)
            self.assertIn("KeyID=", response.location)
            self.assertIn("Expires=", response.location)

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    container[doc_resource]["id"],
                    self.tender_token,
                    container[doc_resource]["key"],
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"],
                "Can't view bid documents in current (active.tendering) tender status",
            )

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?download={}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    container[doc_resource]["id"],
                    container[doc_resource]["key"],
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")
            self.assertEqual(
                response.json["errors"][0]["description"],
                "Can't view bid documents in current (active.tendering) tender status",
            )

    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    def test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.bid_token,
                        container[doc_resource]["key"],
                    )
                )
                self.assertEqual(response.status, "302 Moved Temporarily")
                self.assertIn("http://localhost/get/", response.location)
                self.assertIn("Signature=", response.location)
                self.assertIn("KeyID=", response.location)

        for doc_resource in ["documents", "eligibility_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.tender_token,
                        container[doc_resource]["key"],
                    )
                )
                self.assertEqual(response.status, "302 Moved Temporarily")
                self.assertIn("http://localhost/get/", response.location)
                self.assertIn("Signature=", response.location)
                self.assertIn("KeyID=", response.location)

        for doc_resource in ["financial_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.tender_token,
                        container[doc_resource]["key"],
                    ),
                    status=403,
                )
                self.assertEqual(response.status, "403 Forbidden")
                self.assertEqual(
                    response.json["errors"][0]["description"],
                    "Can't view bid documents in current ({}) tender status".format(status),
                )

        # for doc_resource in ['documents', 'eligibility_documents']:
        # for container in private_doc_id_by_type, doc_id_by_type:
        # response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}'.format(
        # self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
        # self.assertEqual(response.status, '200 OK')

        for doc_resource in ["financial_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?download={}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        container[doc_resource]["key"],
                    ),
                    status=403,
                )
                self.assertEqual(response.status, "403 Forbidden")
                self.assertEqual(
                    response.json["errors"][0]["description"],
                    "Can't view bid documents in current ({}) tender status".format(status),
                )

    test_bids_documents_after_tendering_resource(
        self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification"
    )

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    # qualify bids
    for qualification in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    test_bids_documents_after_tendering_resource(
        self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification.stand-still"
    )

    self.time_shift("active.auction")
    self.check_chronograph()
    test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]

    # posting auction urls
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender_lots = response.json["data"]["lots"]
    self.app.patch_json(
        "/tenders/{}/auction/{}".format(self.tender_id, tender_lots[0]["id"]),
        {
            "data": {
                "lots": [{"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in tender_lots],
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
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, tender_lots[0]["id"]),
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": lot["relatedLot"]} for lot in b["lotValues"]]}
                    for b in auction_bids_data
                ]
            }
        },
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))

    def test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.bid_token,
                        container[doc_resource]["key"],
                    )
                )
                self.assertEqual(response.status, "302 Moved Temporarily")
                self.assertIn("http://localhost/get/", response.location)
                self.assertIn("Signature=", response.location)
                self.assertIn("KeyID=", response.location)

        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get(
                    "/tenders/{}/bids/{}/{}/{}?acc_token={}&download={}".format(
                        self.tender_id,
                        self.bid_id,
                        doc_resource,
                        container[doc_resource]["id"],
                        self.tender_token,
                        container[doc_resource]["key"],
                    )
                )
                self.assertEqual(response.status, "302 Moved Temporarily")
                self.assertIn("http://localhost/get/", response.location)
                self.assertIn("Signature=", response.location)
                self.assertIn("KeyID=", response.location)

        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?download={}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    doc_id_by_type[doc_resource]["id"],
                    doc_id_by_type[doc_resource]["key"],
                )
            )
            self.assertEqual(response.status, "302 Moved Temporarily")
            self.assertIn("http://localhost/get/", response.location)
            self.assertIn("Signature=", response.location)
            self.assertIn("KeyID=", response.location)

            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?download={}".format(
                    self.tender_id,
                    self.bid_id,
                    doc_resource,
                    private_doc_id_by_type[doc_resource]["id"],
                    private_doc_id_by_type[doc_resource]["key"],
                ),
                status=403,
            )
            self.assertEqual(response.status, "403 Forbidden")

    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification")
    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    test_bids_documents_after_auction_resource(self, doc_id_by_type, private_doc_id_by_type, "active.pre-qualification")


def create_tender_bidder_document_nopending(self):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not in one of statuses ('active',)",
    )

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not in one of statuses ('active',)",
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document because award of bid is not in one of statuses ('active',)",
    )


# TenderBidDocumentResourceTest


def patch_tender_bidder_document_private_json(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )

        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )


def put_tender_bidder_document_private_json(self):
    doc_id_by_type = {}
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}
        self.assertEqual("buyerOnly", response.json["data"]["confidentiality"])
        self.assertEqual(
            "Only our company sells badgers with pink hair.", response.json["data"]["confidentialityRationale"]
        )
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "public",
                    "confidentialityRationale": None,
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        self.assertEqual("public", response.json["data"]["confidentiality"])
        self.assertNotIn("confidentialityRationale", response.json["data"])
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    # allow document upload
    self.append_24hours_milestone(self.bid_id)

    self.app.authorization = ("Basic", ("broker", ""))
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.put_json(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token
            ),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document confidentiality in current (active.qualification) tender status",
        )


def get_tender_bidder_document_ds(self):
    doc_id_by_type = {}

    def document_is_unaccessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker2", ""))
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id), status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def document_is_unaccessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.tender_token),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, resource, doc_id, self.tender_token
            ),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.app.authorization = orig_auth

    def all_documents_are_accessible_for_bid_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        for resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            response = self.app.get(
                "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, self.bid_token)
            )
            self.assertEqual(response.status, "200 OK")
            doc1 = response.json["data"][0]
            doc2 = response.json["data"][1]
            self.assertEqual(doc1["title"], "name_{}.doc".format(resource[:-1]))
            self.assertEqual(doc2["title"], "name_{}_private.doc".format(resource[:-1]))
            self.assertEqual(doc1["confidentiality"], "public")
            self.assertEqual(doc2["confidentiality"], "buyerOnly")
            self.assertIn("url", doc1)
            self.assertIn("url", doc2)
            doc_id = doc_id_by_type[resource]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            doc = response.json["data"]
            doc.pop("previousVersions", None)
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource + "private"]["id"]
            response = self.app.get(
                "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                    self.tender_id, self.bid_id, resource, doc_id, self.bid_token
                )
            )
            self.assertEqual(response.status, "200 OK")
            doc = response.json["data"]
            doc.pop("previousVersions", None)
            self.assertEqual(doc, doc2)
        self.app.authorization = orig_auth

    def documents_are_accessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        token = self.tender_token
        response = self.app.get(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, token)
        )
        self.assertEqual(response.status, "200 OK")
        doc_id = doc_id_by_type[resource]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertIn("url", response.json["data"])
        self.assertEqual(response.status, "200 OK")
        doc_id = doc_id_by_type[resource + "private"]["id"]
        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, resource, doc_id, token)
        )
        self.assertEqual(response.status, "200 OK")
        self.assertIn("url", response.json["data"])
        self.app.authorization = orig_auth

    def public_documents_are_accessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker2", ""))

        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, resource))
        self.assertEqual(response.status, "200 OK")
        self.assertIn(doc_id_by_type[resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, resource, doc_id_by_type[resource]["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}.doc".format(resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], "public")
        self.assertEqual(response.json["data"]["format"], "application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(
                self.tender_id, self.bid_id, resource, doc_id_by_type[resource + "private"]["id"]
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["confidentiality"], "buyerOnly")
        self.assertNotIn("url", response.json["data"])

        self.app.authorization = orig_auth

    def all_public_documents_are_accessible_for_others():
        for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
            public_documents_are_accessible_for_others(doc_resource)

    # active.tendering
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "public",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])
        self.assertEqual("name_{}.doc".format(doc_resource[:-1]), response.json["data"]["title"])
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource] = {"id": doc_id, "key": key}

        response = self.app.post_json(
            "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_resource, self.bid_token),
            {
                "data": {
                    "title": "name_{}_private.doc".format(doc_resource[:-1]),
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "confidentiality": "buyerOnly",
                    "confidentialityRationale": "Only our company sells badgers with pink hair.",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        doc_id = response.json["data"]["id"]
        key = self.get_doc_id_from_url(response.json["data"]["url"])
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}
        doc_id_by_type[doc_resource + "private"] = {"id": doc_id, "key": key}

        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    all_documents_are_accessible_for_bid_owner(doc_resource)
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    # switch to active.pre-qualification
    self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    with change_auth(self.app, ("Basic", ("anon", ""))):
        response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for bid in response.json["data"]:
        for lot_value in bid["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )

    for doc_resource in ["documents", "eligibility_documents"]:
        response = self.app.get("/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, doc_resource))
        self.assertEqual(response.status, "200 OK")
        self.assertIn("url", response.json["data"][0])
        self.assertIn(doc_id_by_type[doc_resource]["key"], response.json["data"][0]["url"])
        self.assertNotIn("url", response.json["data"][1])

    for doc_resource in ["documents", "eligibility_documents"]:
        doc_id = doc_id_by_type[doc_resource]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], "public")
        self.assertEqual(response.json["data"]["format"], "application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

        doc_id = doc_id_by_type[doc_resource + "private"]["id"]
        response = self.app.get("/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["title"], "name_{}_private.doc".format(doc_resource[:-1]))
        self.assertEqual(response.json["data"]["confidentiality"], "buyerOnly")
        self.assertEqual(response.json["data"]["format"], "application/msword")
        self.assertEqual(response.json["data"]["language"], "uk")

    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # qualify bids
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    with change_auth(self.app, ("Basic", ("token", ""))):
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualification["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for bid in response.json["data"]:
        for lot_value in bid["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], "public")
    self.assertEqual(response.json["data"]["format"], "application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.auction
    self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        {"id", "status", "tenderers", "lotValues", "items"},
    )
    for bid in response.json["data"]:
        for lot_value in bid["lotValues"]:
            self.assertEqual(
                lot_value.keys(),
                {"relatedLot", "status"},
            )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        {"id", "status", "documents", "eligibilityDocuments", "tenderers", "lotValues", "items"},
    )
    for lot_value in response.json["data"]["lotValues"]:
        self.assertEqual(
            lot_value.keys(),
            {"relatedLot", "status"},
        )
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertIn(doc_id_by_type["documents"]["key"], response.json["data"][0]["url"])
    doc_id = doc_id_by_type["documents"]["id"]
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "name_document.doc")
    self.assertEqual(response.json["data"]["confidentiality"], "public")
    self.assertEqual(response.json["data"]["format"], "application/msword")
    for doc_resource in ["financial_documents", "qualification_documents"]:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ["documents", "eligibility_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to qualification
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    assert_data = [
        "date",
        "status",
        "id",
        "lotValues",
        "tenderers",
        "documents",
        "eligibilityDocuments",
        "qualificationDocuments",
        "financialDocuments",
        "selfQualified",
        "submissionDate",
        "items",
    ]
    assert_data_less = ["date", "status", "id", "lotValues", "tenderers", "selfQualified", "submissionDate", "items"]
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        assert_data.append("selfEligible")
        assert_data_less.append("selfEligible")
    self.assertEqual(
        set(response.json["data"][0].keys()),
        set(assert_data),
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        set(assert_data_less),
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_data),
    )

    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    # get awards
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    self.app.authorization = ("Basic", ("broker", ""))
    self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        set(assert_data),
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        set(assert_data_less),
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_data),
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()

    self.set_status("complete")

    self.app.authorization = ("Basic", ("anon", ""))
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(
        set(response.json["data"][0].keys()),
        set(assert_data),
    )
    self.assertEqual(
        set(response.json["data"][1].keys()),
        set(assert_data_less),
    )
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(
        set(response.json["data"].keys()),
        set(assert_data),
    )
    all_documents_are_accessible_for_bid_owner(doc_resource)
    for doc_resource in ["documents", "financial_documents", "eligibility_documents", "qualification_documents"]:
        documents_are_accessible_for_tender_owner(doc_resource)
    all_public_documents_are_accessible_for_others()


def create_tender_bid_with_all_documents(self):
    docs = [
        {
            "title": "first.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
        {
            "title": "second.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
        {
            "title": "third.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        },
    ]
    bid_data = deepcopy(self.bid_data_wo_docs)
    bid_data["documents"] = docs
    bid_data["qualificationDocuments"] = deepcopy(docs)
    bid_data["eligibilityDocuments"] = deepcopy(docs)
    bid_data["financialDocuments"] = deepcopy(docs)
    set_bid_items(self, bid_data)
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bidder = response.json["data"]
    self.assertEqual(bidder["tenderers"][0]["name"], self.bid_data_wo_docs["tenderers"][0]["name"])
    self.assertIn("id", bidder)
    self.bid_id = bidder["id"]
    self.bid_token = response.json["access"]["token"]
    self.assertIn(bidder["id"], response.headers["Location"])

    documents = bidder["documents"]
    ids = [doc["id"] for doc in documents]
    self.assertEqual(["first.doc", "second.doc", "third.doc"], [document["title"] for document in documents])

    eligibility_documents = bidder["eligibilityDocuments"]
    eligibility_ids = [doc["id"] for doc in eligibility_documents]
    self.assertEqual(
        ["first.doc", "second.doc", "third.doc"], [document["title"] for document in eligibility_documents]
    )

    qualification_documents = bidder["qualificationDocuments"]
    qualification_ids = [doc["id"] for doc in qualification_documents]
    self.assertEqual(
        ["first.doc", "second.doc", "third.doc"], [document["title"] for document in qualification_documents]
    )

    financial_documents = bidder["financialDocuments"]
    financial_ids = [doc["id"] for doc in financial_documents]
    self.assertEqual(["first.doc", "second.doc", "third.doc"], [document["title"] for document in financial_documents])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/eligibility_documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(eligibility_ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/qualification_documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(qualification_ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/financial_documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(financial_ids, [doc["id"] for doc in response.json["data"]])


def create_tender_bid_with_eligibility_document_invalid(self):
    self.docs_container = "eligibilityDocuments"
    self.docs_container_url = "eligibility_documents"
    create_tender_bid_with_document_invalid(self)


def create_tender_bid_with_financial_document_invalid(self):
    self.docs_container = "financialDocuments"
    self.docs_container_url = "financial_documents"
    create_tender_bid_with_document_invalid(self)


def create_tender_bid_with_qualification_document_invalid(self):
    self.docs_container = "qualificationDocuments"
    self.docs_container_url = "qualification_documents"
    create_tender_bid_with_document_invalid(self)


def create_tender_bid_with_eligibility_document(self):
    self.docs_container = "eligibilityDocuments"
    self.docs_container_url = "eligibility_documents"
    create_tender_bid_with_document(self)


def create_tender_bid_with_qualification_document(self):
    self.docs_container = "qualificationDocuments"
    self.docs_container_url = "qualification_documents"
    create_tender_bid_with_document(self)


def create_tender_bid_with_financial_document(self):
    self.docs_container = "financialDocuments"
    self.docs_container_url = "financial_documents"
    create_tender_bid_with_document(self)


def create_tender_bid_with_financial_documents(self):
    self.docs_container = "financialDocuments"
    self.docs_container_url = "financial_documents"
    create_tender_bid_with_documents(self)


def create_tender_bid_with_eligibility_documents(self):
    self.docs_container = "eligibilityDocuments"
    self.docs_container_url = "eligibility_documents"
    create_tender_bid_with_documents(self)


def create_tender_bid_with_qualification_documents(self):
    self.docs_container = "qualificationDocuments"
    self.docs_container_url = "qualification_documents"
    create_tender_bid_with_documents(self)
