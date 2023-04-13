# -*- coding: utf-8 -*-
from copy import deepcopy

import mock
from datetime import timedelta

from openprocurement.api.constants import GUARANTEE_ALLOWED_TENDER_TYPES
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues


# TenderBidResourceTest


def create_tender_bid_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids", {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

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
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {
                        "contactPoint": ["This field is required."],
                        "identifier": {"scheme": ["This field is required."], "id": ["This field is required."]},
                        "name": ["This field is required."],
                        "address": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "tenderers",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}]}}, status=422
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
                    }
                ],
                "location": "body",
                "name": "tenderers",
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": {"tenderers": [test_tender_below_organization]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "value"}],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500, "valueAddedTaxIncluded": False}}},
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
                    "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
                ],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500, "currency": "USD"}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["currency of bid should be identical to currency of value of tender"],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"tenderers": test_tender_below_organization, "value": {"amount": 500}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])


def create_tender_bid(self):
    dateModified = self.mongodb.tenders.get(self.tender_id).get("dateModified")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500},
                  "lotValues": None, "parameters": None, "documents": None}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    self.assertEqual(self.mongodb.tenders.get(self.tender_id).get("dateModified"), dateModified)

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def patch_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "tenderers": [test_tender_below_organization], "status": "draft",
            "value": {"amount": 500},
            "lotValues": None, "parameters": None, "documents": None,
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 600}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["value of bid should be less than value of tender"],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"tenderers": [{"name": "Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 500}, "tenderers": [test_tender_below_organization]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], bid["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bid["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {
            "value": {"amount": 450},
            "lotValues": None, "parameters": None,
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 450)
    self.assertNotEqual(response.json["data"]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {
            "status": "draft",
            "value": {"amount": 400},
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], bid["date"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"status": "draft"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid to (draft) status")

    response = self.app.patch_json(
        "/tenders/{}/bids/some_id".format(self.tender_id), {"data": {"value": {"amount": 400}}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.patch_json("/tenders/some_id/bids/some_id", {"data": {"value": {"amount": 400}}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], token),
        {"data": {"value": {"amount": 400}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


def get_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

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

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    bid_data = response.json["data"]
    # self.assertIn(u'participationUrl', bid_data)
    # bid_data.pop(u'participationUrl')
    self.assertEqual(bid_data, bid)

    response = self.app.get("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.get("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't delete bid in current (active.qualification) tender status"
    )


def delete_tender_bid(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], bid)

    revisions = self.mongodb.tenders.get(self.tender_id).get("revisions")
    self.assertTrue(any([i for i in revisions[-2]["changes"] if i["op"] == "remove" and i["path"] == "/bids"]))
    self.assertTrue(any([i for i in revisions[-1]["changes"] if i["op"] == "add" and i["path"] == "/bids"]))

    response = self.app.delete("/tenders/{}/bids/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.delete("/tenders/some_id/bids/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_tenderers(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    response = self.app.get("/tenders/{}/bids".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bids in current (active.tendering) tender status"
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], bid)

    response = self.app.get("/tenders/some_id/bids", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def bid_Administrator_change(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))
    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": {"tenderers": [{"identifier": {"id": "00000000"}}], "value": {"amount": 400}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["id"], "00000000")


def create_tender_bid_no_scale_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = {
        "data": {
            "value": {"amount": 500},
            "tenderers": [{key: value for key, value in test_tender_below_organization.items() if key != "scale"}],
        }
    }
    response = self.app.post_json(request_path, bid_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"scale": ["This field is required."]}], "location": "body", "name": "tenderers"}],
    )


@mock.patch("openprocurement.tender.core.procedure.models.organization.ORGANIZATION_SCALE_FROM", get_now() + timedelta(days=1))
def create_tender_bid_with_scale_not_required(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = {"data": {"value": {"amount": 500}, "tenderers": [test_tender_below_organization]}}
    response = self.app.post_json(request_path, bid_data)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("scale", response.json["data"])


@mock.patch("openprocurement.tender.core.procedure.models.organization.ORGANIZATION_SCALE_FROM", get_now() + timedelta(days=1))
def create_tender_bid_no_scale(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = {
        "data": {
            "value": {"amount": 500},
            "tenderers": [{key: value for key, value in test_tender_below_organization.items() if key != "scale"}],
        }
    }
    response = self.app.post_json(request_path, bid_data)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("scale", response.json["data"]["tenderers"][0])


# Tender2LotBidResourceTest


def patch_tender_with_bids_lots_none(self):
    bid = self.test_bids_data[0].copy()
    lots = self.mongodb.tenders.get(self.tender_id).get("lots")

    set_bid_lotvalues(bid, lots)

    self.create_bid(self.tender_id, bid)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"lots": None}},
        status=403
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update tender in current (active.tendering) status"
            }
        ]
    )


def patch_tender_lot_values_any_order(self):
    lots = self.mongodb.tenders.get(self.tender_id).get("lots")

    bid = deepcopy(self.test_bids_data[0])
    value_1 = bid.pop("value", None)
    value_2 = deepcopy(value_1)
    value_2["amount"] = 453

    # applying for the first lot
    bid["lotValues"] = [{"value": value_1, "relatedLot": lots[0]["id"]}]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    bid_id = response.json["data"]["id"]
    token = response.json["access"]["token"]

    self.assertEqual(len(response.json["data"]["lotValues"]), 1)
    self.assertIn("date", response.json["data"]["lotValues"][0])
    expected_status = response.json["data"]["lotValues"][0].get("status")

    # applying for the second lot
    bid["lotValues"] = [
        {"value": value_2, "relatedLot": lots[1]["id"]},
        {"value": value_1, "relatedLot": lots[0]["id"]},
    ]
    response = self.app.patch_json(f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={token}", {"data": bid})
    self.assertEqual(len(response.json["data"]["lotValues"]), 2)
    self.assertIn("date", response.json["data"]["lotValues"][0])
    self.assertIn("date", response.json["data"]["lotValues"][1])
    self.assertEqual(response.json["data"]["lotValues"][0].get("status"), expected_status)
    self.assertEqual(response.json["data"]["lotValues"][1].get("status"), expected_status)
    self.assertEqual(value_2["amount"], response.json["data"]["lotValues"][0]["value"]["amount"])
    self.assertEqual(value_1["amount"], response.json["data"]["lotValues"][1]["value"]["amount"])

# TenderBidFeaturesResourceTest


def features_bid(self):
    test_features_bids = [
        {
            "parameters": [{"code": i["code"], "value": 0.1} for i in self.initial_data["features"]],
            "status": "active",
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
        {
            "parameters": [{"code": i["code"], "value": 0.15} for i in self.initial_data["features"]],
            "tenderers": [test_tender_below_organization],
            "status": "draft",
            "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
    ]
    for i in test_features_bids:
        bid, bid_token = self.create_bid(self.tender_id, i)
        bid.pop("date")
        bid.pop("id")
        for k in ("documents", "lotValues"):
            self.assertEqual(bid.pop(k, []), [])
        self.assertEqual(bid, i)


def features_bid_invalid(self):
    data = {
        "tenderers": [test_tender_below_organization],
        "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
    }
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "parameters"}],
    )
    data["parameters"] = [{"code": "OCDS-123454-AIR-INTAKE", "value": 0.1}]
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["All features parameters is required."], "location": "body", "name": "parameters"}],
    )
    data["parameters"].append({"code": "OCDS-123454-AIR-INTAKE", "value": 0.1})
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Parameter code should be uniq for all parameters"],
                "location": "body",
                "name": "parameters",
            }
        ],
    )
    data["parameters"][1]["code"] = "OCDS-123454-YEARS"
    data["parameters"][1]["value"] = 0.2
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"value": ["value should be one of feature value."]}],
                "location": "body",
                "name": "parameters",
            }
        ],
    )


# TenderBidDocumentResourceTest


def not_found(self):
    document = {
        "data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    }
    response = self.app.post_json(
        "/tenders/some_id/bids/some_id/documents",
        document,
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.post_json(
        "/tenders/{}/bids/some_id/documents".format(self.tender_id),
        document,
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.get("/tenders/some_id/bids/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/bids/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.get("/tenders/some_id/bids/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/bids/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.get("/tenders/{}/bids/{}/documents/some_id".format(self.tender_id, self.bid_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )

    response = self.app.put_json(
        "/tenders/some_id/bids/some_id/documents/some_id",
        document,
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.put_json(
        "/tenders/{}/bids/some_id/documents/some_id".format(self.tender_id),
        document,
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/some_id".format(self.tender_id, self.bid_id),
        document,
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )

    # self.app.authorization = ("Basic", ("invalid", ""))
    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/some_id".format(self.tender_id, self.bid_id),
        document,
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


def update_tender_bid_document_invalid_pmr(self):
    requirement = self.app.get(
        "/tenders/{}".format(self.tender_id)
    ).json["data"]["criteria"][0]["requirementGroups"][0]["requirements"][0]

    self.rr_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": requirement["id"],
            "title": requirement["title"],
        },
        "value": "True",
    }]

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}, "status": "draft"}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]
    bid_id = bid["id"]

    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": self.rr_data},
    )
    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "active"}}
    )

    document = {
        "data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
        document,
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    # make tender procurementMethodRationale simple
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "simple"
    self.mongodb.tenders.save(doc)

    # make tender status active.qualification
    self.set_status("active.qualification")

    # add bid award in status pending
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": bid_id,
                "value": {
                    "amount": 500,

                },
            }
        },
    )
    self.app.authorization = auth
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # negative put
    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
        document,
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], 
        "Can't upload document with ('active.qualification',) tender status and procurementMethodRationale simple"
    )

    # positive put
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "Open"
    self.mongodb.tenders.save(doc)

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
        document,
        status=200,
    )
    self.assertEqual(response.status, "200 OK")

    # negative patch
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "simple"
    self.mongodb.tenders.save(doc)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't upload document with ('active.qualification',) tender status and procurementMethodRationale simple"
    )

    # positive patch
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "Open"
    self.mongodb.tenders.save(doc)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
        {"data": {"description": "document description123"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description123", response.json["data"]["description"])


def update_tender_bid_pmr_related_doc(self):
    criteria = self.app.get(
        "/tenders/{}".format(self.tender_id)
    ).json["data"]["criteria"]
    requirement = criteria[0]["requirementGroups"][0]["requirements"][0]

    evidences = [{
        "relatedDocument": {
            "id": "a" * 32,
            "title": "name.doc"
        },
        "type": "document",
        "id": "f77bda2a24e74f5286ede23cbe8f6b1e",
        "title": "вид та умови надання забезпечення гарантія1"
    }]

    rr_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": requirement["id"],
            "title": requirement["title"],
        },
        "value": "True",
        "evidences": evidences
    }]

    # POST
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "requirementResponses": rr_data,
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 500},
        }},
    )
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}",
        {"data": {"status": "active"}},
        status=422
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "requirementResponses",
         "description": [{"evidences": [{"relatedDocument": ["relatedDocument.id should be one of bid documents"]}]}]}
    )

    # you cannot set document.id, so you cannot post requirementResponses with relatedDocument.id
    del rr_data[0]["evidences"]
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "requirementResponses": rr_data,
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 500},
            "documents": [
                {
                    "id": "a" * 32,
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            ]
        }},
    )
    bid = response.json["data"]
    bid_id = bid["id"]
    bid_token = response.json["access"]["token"]

    # patch invalid
    rr_data[0]["evidences"] = evidences
    rr_data[0]["evidences"][0]["relatedDocument"]["id"] = "b" * 32
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}",
        {"data": {"requirementResponses": rr_data, "status": "active"}},
        status=422
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "requirementResponses",
         "description": [{"evidences": [{"relatedDocument": ["relatedDocument.id should be one of bid documents"]}]}]}
    )

    # patch valid relatedDocument.id
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_data[0]["evidences"][0]["relatedDocument"]["id"] = response.json["data"]["id"]

    self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}",
        {"data": {"requirementResponses": rr_data}},
        status=200
    )


def update_tender_bid_pmr_related_tenderer(self):
    criteria = self.app.get(
        "/tenders/{}".format(self.tender_id)
    ).json["data"]["criteria"]
    requirement = criteria[0]["requirementGroups"][0]["requirements"][0]

    rr_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": requirement["id"],
            "title": requirement["title"],
        },
        "value": "True",
        "relatedTenderer": {"id": "abc", "title": ""},
    }]

    # POST
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "status": "active",
            "requirementResponses": rr_data,
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 500},
        }},
        status=422
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "requirementResponses",
         "description": [{"relatedTenderer": ["relatedTenderer should be one of bid tenderers"]}]}
    )


def update_tender_rr_evidence_id(self):
    criteria = self.app.get(
        "/tenders/{}".format(self.tender_id)
    ).json["data"]["criteria"]
    requirement = criteria[0]["requirementGroups"][0]["requirements"][0]

    evidences = [{
        "description": "2",
        "id": "a" * 32,
        "relatedDocument": None,
        "title": "4",
        "type": "statement"
    }]

    rr_data = [{
        "id": "f" * 32,
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": requirement["id"],
            "title": requirement["title"],
        },
        "value": "True",
        "evidences": evidences
    }]

    # POST with passed ids
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {
            "requirementResponses": rr_data,
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 500},
        }}
    )
    bid = response.json["data"]
    token = response.json["access"]["token"]
    rr = bid["requirementResponses"][0]
    self.assertEqual(rr["id"], "f" * 32)
    self.assertEqual(rr["evidences"][0]["id"], "a" * 32)

    # PATCH with changes to ids
    rr_data[0]["id"] = "c" * 32
    rr_data[0]["description"] = "changed description"
    rr_data[0]["evidences"][0]["id"] = "b" * 32
    rr_data[0]["evidences"][0]["description"] = "changed description"
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={token}",
        {"data": {
            "requirementResponses": rr_data,
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 500},
        }}
    )
    rr = response.json["data"]["requirementResponses"][0]
    self.assertEqual(rr["id"], "c" * 32)
    self.assertEqual(rr["evidences"][0]["id"], "b" * 32)


def patch_tender_bid_document(self):
    document = {
        "data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        document,
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, "invalid-token"),
        {"data": {}},
        status=403,
    )
    self.assertEqual(
        response.json,
        {'status': 'error', 'errors': [{'location': 'url', 'name': 'permission', 'description': 'Forbidden'}]}
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
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
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
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
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    self.set_status("active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (active.awarded) tender status"
    )


def create_tender_bid_document_nopending(self):
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"requirementResponses": self.rr_data, "tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
    )
    bid = response.json["data"]
    token = response.json["access"]["token"]
    bid_id = bid["id"]

    document = {
        "data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        document,
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.set_status("active.qualification")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document because award of bid is not in pending state"
    )

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, token),
        document,
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document because award of bid is not in pending state"
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        document,
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document because award of bid is not in pending state"
    )


def create_tender_bid_document_invalid_pmr(self):
    requirement = self.app.get(
        "/tenders/{}".format(self.tender_id)
    ).json["data"]["criteria"][0]["requirementGroups"][0]["requirements"][0]

    self.rr_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": requirement["id"],
            "title": requirement["title"],
        },
        "value": "True",
    }]
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}, "status": "draft"}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    token = response.json["access"]["token"]
    bid_id = bid["id"]

    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, token),
        {"data": self.rr_data},
    )
    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, token),
        {"data": {"status": "active"}}
    )

    # make tender procurementMethodRationale simple
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "simple"
    self.mongodb.tenders.save(doc)

    # make tender status active.qualification
    self.set_status("active.qualification")

    # add bid award in status pending
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/awards".format(self.tender_id),
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": bid_id,
                "value": {
                    "amount": 500,
                    
                },
            }
        },
    )
    self.app.authorization = auth
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
   
    # negative
    document = {
        "data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        document,
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], 
        "Can't upload document with ('active.qualification',) tender status and procurementMethodRationale simple"
    )
    
    # positive
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "Open"
    self.mongodb.tenders.save(doc)
    
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, token),
        document,
        status=201,
    )
    self.assertEqual(response.status, "201 Created")
    
    
# TenderBidDocumentWithDSResourceTest


def create_tender_bid_document_json(self):
    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, "invalid-token"),
        {
            "data": document
        },
        status=403,
    )
    self.assertEqual(
        response.json,
        {'status': 'error', 'errors': [{'location': 'url', 'name': 'permission', 'description': 'Forbidden'}]}
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": document
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    uid = self.get_doc_id_from_url(document["url"])

    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status",
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents?all=true&acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download=some_id&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, self.bid_token
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}".format(self.tender_id, self.bid_id, doc_id, uid), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status"
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, uid, self.bid_token
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status"
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

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
    self.assertIn(response.json["data"]["id"], response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    self.set_status("active.awarded")

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
        response.json["errors"][0]["description"], "Can't add document in current (active.awarded) tender status"
    )

    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("http://localhost/get/", response.json["data"]["url"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, uid, self.bid_token
        )
    )
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)


def create_tender_bid_document_json_bulk(self):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                },
                {
                    "title": "name2.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]

    def assert_document(document, title):
        self.assertEqual(title, document["title"])

    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    response = self.app.get(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")


def create_one_tender_bid_document_json_bulk(self):
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIsInstance(response.json["data"], list)
    self.assertEqual(len(response.json["data"]), 1)


def create_tender_bid_document_with_award_json(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    procurementMethodType = response.json["data"]["procurementMethodType"]
    if procurementMethodType not in GUARANTEE_ALLOWED_TENDER_TYPES:
        return

    # self.app.authorization = ("Basic", ("token", ""))
    #  It works because (Allow, "g:admins", ALL_PERMISSIONS), but should admins post documents ?
    # probably should not, but seems it was for adding the award below
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {
            "title": "test.doc",
            "url": self.generate_docservice_url(),
            "format": "application/msword",
            "documentType": "biddingDocuments",
            "hash": "md5:" + "0" * 32
        }},
        status=201
    )
    doc_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(self.tender_id, self.bid_id,
                                                                                     self.rr_guarantee_id,
                                                                                     self.bid_token),
        {"data": {
            "title": "Документальне підтвердження",
            "description": "Довідка в довільній формі",
            "type": "document",
            "relatedDocument": {
                "id": doc_id,
                "title": "test.doc"
            },
        }}, status=403
    )

    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [
        {
            "location": "body",
            "name": "data",
            "description": "available only in ['active.awarded', 'active.qualification'] statuses"
        }
    ])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/requirement_responses/{}?acc_token={}".format(self.tender_id, self.bid_id,
                                                                                     self.rr_guarantee_id,
                                                                                     self.bid_token),
        {"data": {
            "evidences": [{
                "title": "Документальне підтвердження",
                "description": "Довідка в довільній формі",
                "type": "document",
                "relatedDocument": {
                    "id": doc_id,
                    "title": "test.doc"
                },
            }]
        }}, status=422
    )
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [
        {
            "location": "body",
            "name": "evidences",
            "description": [
                "available only in ['active.awarded', 'active.qualification'] status"
            ]
        }
    ])

    with change_auth(self.app, ("Basic", ("token", ""))):  # this copied from above
        self.set_status("active.qualification")
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.bid_id,
            }},
        )
    award = response.json["data"]
    award_id = award["id"]
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active"}}, status=200)

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {
            "title": "test.doc",
            "url": self.generate_docservice_url(),
            "format": "application/msword",
            "hash": "md5:" + "0" * 32
        }},
        status=201
    )

    doc_id = response.json["data"]["id"]
    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(self.tender_id, self.bid_id,
                                                                                     self.rr_guarantee_id,
                                                                                     self.bid_token),
        {"data": {
            "title": "Документальне підтвердження",
            "description": "Довідка в довільній формі",
            "type": "document",
            "relatedDocument": {
                "id": doc_id
            }
        }}, status=201
    )


def create_tender_bid_document_active_qualification(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    if response.json["data"]["procurementMethodType"] not in GUARANTEE_ALLOWED_TENDER_TYPES:
        return

    with change_auth(self.app, ("Basic", ("token", ""))):  # this copied from above
        self.set_status("active.qualification")
        self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.bid_id,
            }},
            status=201
        )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {
            "title": "test.doc",
            "url": self.generate_docservice_url(),
            "format": "application/msword",
            "hash": "md5:" + "0" * 32
        }},
        status=403
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data",
          "description": "Can't upload document with ('active.qualification',) tender status "
                         "and procurementMethodRationale simple"}]
    )


def create_tender_bid_document_with_award_json_bulk(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    procurementMethodType = response.json["data"]["procurementMethodType"]
    if procurementMethodType not in GUARANTEE_ALLOWED_TENDER_TYPES:
        return

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "contractGuarantees",
                },
                {
                    "title": "name2.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "contractGuarantees",
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]

    def assert_document(document, title, type):
        self.assertEqual(title, document["title"])
        self.assertEqual(type, document["documentType"])

    assert_document(doc_1, "name1.doc", "contractGuarantees")
    assert_document(doc_2, "name2.doc", "contractGuarantees")

    for doc_id in [doc_1["id"], doc_2["id"]]:
        response = self.app.post_json(
            "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(
                self.tender_id, self.bid_id, self.rr_guarantee_id, self.bid_token
            ),
            {"data": {
                "title": "Документальне підтвердження",
                "description": "Довідка в довільній формі",
                "type": "document",
                "relatedDocument": {
                    "id": doc_1,
                    "title": "test.doc"
                },
            }}, status=403
        )

        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["errors"], [
            {
                "location": "body",
                "name": "data",
                "description": "available only in ['active.awarded', 'active.qualification'] statuses"
            }
        ])

    self.set_status("active.qualification")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "bid_id": self.bid_id,
            }},
        )
    award = response.json["data"]
    award_id = award["id"]
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_id, self.tender_token),
        {"data": {"status": "active"}}, status=200)

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "contractGuarantees",
                },
                {
                    "title": "name2.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "contractGuarantees",
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]

    def assert_document(document, title, type):
        self.assertEqual(title, document["title"])
        self.assertEqual(type, document["documentType"])

    assert_document(doc_1, "name1.doc", "contractGuarantees")
    assert_document(doc_2, "name2.doc", "contractGuarantees")

    for doc_id in [doc_1["id"], doc_2["id"]]:
        self.app.post_json(
            "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(
                self.tender_id, self.bid_id, self.rr_guarantee_id, self.bid_token
            ),
            {"data": {
                "title": "Документальне підтвердження",
                "description": "Довідка в довільній формі",
                "type": "document",
                "relatedDocument": {
                    "id": doc_id
                }
            }}, status=201
        )

    response = self.app.get(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    assert_document(doc_1, "name1.doc", "contractGuarantees")
    assert_document(doc_2, "name2.doc", "contractGuarantees")


def put_tender_bid_document_json(self):
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

    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
        "description": "test description",
    }

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, "invalid-token"),
        {"data": document},
        status=403
    )
    self.assertEqual(
        response.json,
        {'status': 'error', 'errors': [{'location': 'url', 'name': 'permission', 'description': 'Forbidden'}]}
    )

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {"data": document},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("test description", response.json["data"]["description"])
    self.assertEqual(doc_id, response.json["data"]["id"])

    uid = self.get_doc_id_from_url(document["url"])
    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, uid, self.bid_token
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

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
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("test description", response.json["data"]["description"])
    self.assertEqual(doc_id, response.json["data"]["id"])

    uid = self.get_doc_id_from_url(document["url"])
    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, uid, self.bid_token
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    self.set_status("active.awarded")

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
        response.json["errors"][0]["description"], "Can't update document in current (active.awarded) tender status"
    )


# TenderBidBatchDocumentWithDSResourceTest


def create_tender_bid_with_document_invalid(self):
    # test requires bid data stored on `bid_data_wo_docs` attribute of test class
    docs = [
        {
            "title": "name.doc",
            "url": "http://invalid.docservice.url/get/uuid",
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    docs_container = self.docs_container if hasattr(self, "docs_container") else "documents"
    bid_data = deepcopy(self.bid_data_wo_docs)
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    docs = [
        {
            "title": "name.doc",
            "url": "/".join(self.generate_docservice_url().split("/")[:4]),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().split("?")[0],
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    docs = [{"title": "name.doc", "url": self.generate_docservice_url(), "format": "application/msword"}]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["location"], "body")
    self.assertEqual(response.json["errors"][0]["name"], "hash")
    self.assertEqual(response.json["errors"][0]["description"], "This field is required.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().replace(list(self.app.app.registry.keyring.keys())[-1], "0" * 8),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url expired.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().replace("Signature=", "Signature=ABC"),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url signature invalid.")

    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url().replace("Signature=", "Signature=bw%3D%3D"),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url invalid.")


def create_tender_bid_with_document(self):
    # test requires bid data stored on `bid_data_wo_docs` attribute of test class
    docs = [
        {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    docs_container = self.docs_container if hasattr(self, "docs_container") else "documents"
    docs_container_url = self.docs_container_url if hasattr(self, "docs_container_url") else "documents"
    bid_data = deepcopy(self.bid_data_wo_docs)
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", bid)
    self.bid_id = bid["id"]
    self.bid_token = response.json["access"]["token"]
    self.assertIn(bid["id"], response.headers["Location"])
    document = bid[docs_container][0]
    self.assertEqual("name.doc", document["title"])

    doc_id = self.get_doc_id_from_url(document["url"])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, docs_container_url), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status",
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, docs_container_url, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(document["id"], response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?all=true&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(document["id"], response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?download={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], doc_id
        ),
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid documents in current (active.tendering) tender status"
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], doc_id, self.bid_token
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, docs_container_url, document["id"]), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid documents in current (active.tendering) tender status"
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(document["id"], response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])


def create_tender_bid_with_documents(self):
    # test requires bid data stored on `bid_data_wo_docs` attribute of test class
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
    docs_container = self.docs_container if hasattr(self, "docs_container") else "documents"
    docs_container_url = self.docs_container_url if hasattr(self, "docs_container_url") else "documents"
    bid_data = deepcopy(self.bid_data_wo_docs)
    bid_data[docs_container] = docs
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", bid)
    self.bid_id = bid["id"]
    self.bid_token = response.json["access"]["token"]
    self.assertIn(bid["id"], response.headers["Location"])
    documents = bid[docs_container]
    ids = [doc["id"] for doc in documents]
    self.assertEqual(["first.doc", "second.doc", "third.doc"], [document["title"] for document in documents])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}".format(self.tender_id, self.bid_id, docs_container_url), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status",
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?acc_token={}".format(self.tender_id, self.bid_id, docs_container_url, self.bid_token)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(ids, [doc["id"] for doc in response.json["data"]])

    response = self.app.get(
        "/tenders/{}/bids/{}/{}?all=true&acc_token={}".format(
            self.tender_id, self.bid_id, docs_container_url, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(ids, [doc["id"] for doc in response.json["data"]])

    for index, document in enumerate(documents):
        doc_id = self.get_doc_id_from_url(document["url"])

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
            ),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?download={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], doc_id
            ),
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
                self.tender_id, self.bid_id, docs_container_url, document["id"], doc_id, self.bid_token
            )
        )
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertIn("Expires=", response.location)

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}".format(self.tender_id, self.bid_id, docs_container_url, document["id"]),
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't view bid documents in current (active.tendering) tender status",
        )

        response = self.app.get(
            "/tenders/{}/bids/{}/{}/{}?acc_token={}".format(
                self.tender_id, self.bid_id, docs_container_url, document["id"], self.bid_token
            )
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(document["id"], response.json["data"]["id"])


@mock.patch("openprocurement.tender.core.models.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
@mock.patch("openprocurement.tender.belowthreshold.validation.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
def bid_activate_with_cancelled_tenderer_criterion(self):
    self.set_status("active.enquiries")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    bid_pending_procedures = [
        "aboveThresholdEU",
        "esco",
        "closeFrameworkAgreementUA",
        "competitiveDialogueEU",
        "competitiveDialogueUA",
        "competitiveDialogueEU.stage2",
    ]
    if response.json["data"]["procurementMethodType"] in bid_pending_procedures:
        next_status = "pending"
    else:
        next_status = "active"
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    rrs = []
    for criterion in criteria[:-1]:
        for req in criterion["requirementGroups"][0]["requirements"]:

            if criterion["source"] == "tenderer":
                rrs.append(
                    {
                        "title": "Requirement response",
                        "description": "some description",
                        "requirement": {
                            "id": req["id"],
                            "title": req["title"],
                        },
                        "value": True,
                    },
                )
    rrs = rrs[1:]

    if not hasattr(self, "tender_auth"):
        self.tender_auth = self.app.authorization
    with change_auth(self.app, self.tender_auth) as app:
        criterion_to_cancel = criteria[-1]
        criterion_id = criterion_to_cancel["id"]
        rg_id = criterion_to_cancel["requirementGroups"][0]["id"]
        requirement_ids = [requirement["id"] for requirement in criterion_to_cancel["requirementGroups"][0]["requirements"]]
        requirement_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
        for requirement_id in requirement_ids:
            response = self.app.put_json(
                requirement_url.format(self.tender_id, criterion_id, rg_id, requirement_id, self.tender_token),
                {"data": {"status": "cancelled"}})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")

    self.set_status("active.tendering")
    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": rrs},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
