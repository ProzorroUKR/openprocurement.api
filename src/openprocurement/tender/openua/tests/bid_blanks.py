from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    now,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.core.tests.utils import change_auth

# TenderBidResourceTest


def clean_requirement_responses(rrs: list):
    serialized_fields = {'unit', 'classification'}
    for rr in rrs:
        for field in serialized_fields:
            rr.pop(field, None)


def create_tender_biddder_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/bids",
        {"data": {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}},
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

    response = self.app.post_json(
        request_path,
        {"data": {"selfEligible": True, "selfQualified": True, "tenderers": [{"identifier": "invalid_value"}]}},
        status=422,
    )
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

    response = self.app.post_json(
        request_path,
        {"data": {"selfEligible": True, "selfQualified": True, "tenderers": [{"identifier": {}}]}},
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
                        "identifier": {"scheme": ["This field is required."], "id": ["This field is required."]},
                        "name": ["This field is required."],
                        "address": ["This field is required."],
                        "scale": ["This field is required."],
                    }
                ],
                "location": "body",
                "name": "tenderers",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "selfEligible": True,
                "selfQualified": True,
                "tenderers": [{"name": "name", "identifier": {"uri": "invalid_value"}}],
            }
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
            }
        ],
    )

    bid_data = deepcopy(self.test_bids_data[0])

    # TODO: uncomment when bid activation will be removed

    # response = self.app.post_json(
    #     request_path,
    #     {"data": bid_data},
    #     status=422,
    # )
    #
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [{"description": ["This field is required."], "location": "body", "name": "value"}],
    # )
    #
    # bid_data["value"] = {"amount": 500, "valueAddedTaxIncluded": False}
    #
    # response = self.app.post_json(
    #     request_path,
    #     {"data": bid_data},
    #     status=422,
    # )
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             "description": [
    #                 "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender"
    #             ],
    #             "location": "body",
    #             "name": "value",
    #         }
    #     ],
    # )
    #
    # bid_data["value"] = {"amount": 500, "currency": "USD"}
    # response = self.app.post_json(
    #     request_path,
    #     {"data": bid_data},
    #     status=422,
    # )
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             "description": ["currency of bid should be identical to currency of value of tender"],
    #             "location": "body",
    #             "name": "value",
    #         }
    #     ],
    # )

    bid_data["lotValues"][0]["value"] = {"amount": 500}
    bid_data["tenderers"] = test_tender_below_organization

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("invalid literal for int() with base 10", response.json["errors"][0]["description"])


def create_tender_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update({"parameters": None, "documents": None})
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    self.assertEqual(bid["tenderers"][0]["name"], test_tender_below_organization["name"])
    self.assertIn("id", bid)
    self.assertIn(bid["id"], response.headers["Location"])

    # set tender period in future  # WTF this change, tender in active.tendering
    # data = deepcopy(self.initial_data)
    # data["tenderPeriod"]["endDate"] = (now + timedelta(days=17)).isoformat()
    # data["tenderPeriod"]["startDate"] = (now + timedelta(days=1)).isoformat()
    # response = self.app.patch_json(
    #     "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
    #     {"data": {"tenderPeriod": data["tenderPeriod"]}},
    # )
    # self.assertEqual(response.status, "200 OK")
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["tenderPeriod"] = {
        "startDate": (now + timedelta(days=1)).isoformat(),
        "endDate": (now + timedelta(days=17)).isoformat(),
    }
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Bid can be added only during the tendering period", response.json["errors"][0]["description"])

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (complete) tender status")


def patch_tender_bidder_decimal_problem(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender_value = response.json["data"]["value"]["amount"]
    self.assertEqual(319400.52, tender_value)

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "value": {"amount": tender_value},
            "status": "draft",
        }
    )

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")


def patch_tender_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, self.initial_lots)
    bid_data.update({"status": "draft"})

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]
    lot_values = bid["lotValues"]
    lot_values[0]["value"]["amount"] = 600
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {
            "data": {
                "status": "pending",
                "lotValues": lot_values,
                "parameters": None,
            }
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
                "description": [{"value": ["value of bid should be less than value of lot"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    lot_values[0]["value"]["amount"] = 500
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "pending", "lotValues": lot_values}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "draft"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can't update bid to (draft) status", "location": "body", "name": "bid"}],
    )

    lot_values[0]["value"]["amount"] = 400
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bid['id'], bid_token)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], bid["lotValues"][0]["date"])

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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    self.set_status("complete")

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"lotValues": lot_values}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update bid in current (complete) tender status")


def patch_tender_draft_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "status": "draft",
        }
    )
    set_bid_lotvalues(bid_data, self.initial_lots)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]
    bid_token = response.json["access"]["token"]

    lot_values = bid["lotValues"]
    lov_value_date = lot_values[0]["date"]
    del lot_values[0]["date"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token),
        {"data": {"status": "draft", "lotValues": lot_values}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json, None)

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


def create_bid_after_removing_lot(self):
    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.initial_lots[0]["id"]}]
    bid_data["documents"] = None
    bid_data["parameters"] = None
    bid_data.pop("value")
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data})
    bid, bid_token = response.json["data"], response.json["access"]["token"]
    bid_id = bid["id"]
    self.assertNotIn("documents", bid)
    self.assertNotIn("parameters", bid)

    # removing tender lots
    tender = self.mongodb.tenders.get(self.tender_id)
    del tender["lots"]
    self.mongodb.tenders.save(tender)

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertNotIn("lots", response.json["data"])

    # patch bid to delete lotValues
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}",
        {
            "data": {
                "lotValues": None,
                "value": {"amount": 500},
                "parameters": None,
            }
        },
    )
    data = response.json["data"]
    self.assertEqual(data["value"]["amount"], 500)
    self.assertNotIn("lotValues", data)
    self.assertNotIn("documents", data)
    self.assertNotIn("parameters", data)


def get_tender_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "value": {"amount": 500},
        }
    )
    set_bid_lotvalues(bid_data, self.initial_lots)
    bid, bid_token = self.create_bid(self.tender_id, bid_data)

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
    bid["status"] = "active"
    bid["lotValues"][0]["status"] = "active"

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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], bid_token), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't delete bid in current (active.qualification) tender status"
    )


def delete_tender_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    set_bid_lotvalues(bid_data, self.initial_lots)
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
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
    self.assertTrue(any(i for i in revisions[-2]["changes"] if i["op"] == "remove" and i["path"] == "/bids"))
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

    self.set_status("complete")

    # finished tender does not have deleted bid
    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, bid["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "bid_id"}])


def get_tender_tenderers(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "value": {"amount": 500},
        }
    )
    set_bid_lotvalues(bid_data, self.initial_lots)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def bid_Administrator_change(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    set_bid_lotvalues(bid_data, self.initial_lots)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bid = response.json["data"]

    self.app.authorization = ("Basic", ("administrator", ""))

    patch_bid_data = {}
    patch_bid_data["tenderers"] = bid_data["tenderers"]
    patch_bid_data["tenderers"][0]["identifier"]["id"] = "00000000"
    patch_bid_data["lotValues"] = bid["lotValues"]
    patch_bid_data["lotValues"][0]["value"]["amount"] = 400

    response = self.app.patch_json(
        "/tenders/{}/bids/{}".format(self.tender_id, bid["id"]),
        {"data": patch_bid_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["lotValues"][0]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["tenderers"][0]["identifier"]["id"], "00000000")


def draft1_bid(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "tenderers": [self.test_bids_data[0]["tenderers"][0]],
            "value": {"amount": 500},
            "status": "draft",
        }
    )
    set_bid_lotvalues(bid_data, self.initial_lots)
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("active.auction")
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})

    response = self.check_chronograph()

    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.json["data"], [])


def draft2_bids(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["value"] = {"amount": 500}
    bid_data["status"] = "draft"
    bid_data["tenderers"] = [self.test_bids_data[0]["tenderers"][0]]
    set_bid_lotvalues(bid_data, self.initial_lots)

    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid_data})
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("active.auction")
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})

    response = self.check_chronograph()

    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.json["data"], [])


def bids_activation_on_tender_documents(self):
    bids_access = {}

    # submit bids
    for data in self.test_bids_data:
        bid, bid_token = self.create_bid(self.tender_id, data)
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


def create_tender_bid_no_scale_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {
            "value": {"amount": 500},
            "tenderers": [
                {key: value for key, value in self.test_bids_data[0]["tenderers"][0].items() if key != "scale"}
            ],
        }
    )
    bid_data = {"data": bid_data}
    response = self.app.post_json(request_path, bid_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "tenderers", "description": [{"scale": ["This field is required."]}]}],
    )


# TenderBidResourceTest


def features_bidder(self):
    test_features_bids = deepcopy(self.test_bids_data)
    test_features_bids[0]["parameters"] = [{"code": i["code"], "value": 0.1} for i in self.initial_data["features"]]
    test_features_bids[1].update(
        {
            "parameters": [{"code": i["code"], "value": 0.1} for i in self.initial_data["features"]],
            "status": "pending",
        }
    )
    for i in test_features_bids:
        bid, bid_token = self.create_bid(self.tender_id, i)
        i["status"] = "pending"
        bid.pop("date")
        bid.pop("id")
        bid.pop("submissionDate", None)
        for k in ("documents", "lotValues"):
            self.assertEqual(bid.pop(k, []), [])
        self.assertEqual(bid, i)


def features_bidder_invalid(self):
    data = deepcopy(self.test_bids_data[0])
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "parameters"}],
    )
    data["parameters"] = [{"code": "OCDS-123454-AIR-INTAKE", "value": 0.1}]
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": data}, status=422)
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
    response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": data}, status=422)
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


def patch_tender_bidder_document_json(self):
    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": document},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

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
    self.assertIn(
        response.json["errors"][0]["description"],
        (
            "Can't add document because award of bid is not in one of statuses ('active',)",
            "Can't add document because award of bid is not in one of statuses ('active',)",
        ),
    )


def patch_tender_bidder_document_json(self):
    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": document},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

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
    self.assertIn(
        response.json["errors"][0]["description"],
        (
            "Can't update document because award of bid is not in one of statuses ('active',)",
            "Can't update document because award of bid is not in one of statuses ('active',)",
        ),
    )


# TenderBidDocumentResourceTest
def create_tender_bidder_document_nopending_json(self):
    bid_data = deepcopy(self.test_bids_data[0])
    if getattr(self, "initial_lots"):
        set_bid_lotvalues(bid_data, self.initial_lots)

    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    bid = response.json["data"]
    bid_id = bid["id"]
    bid_token = response.json["access"]["token"]

    document = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": document},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.set_status("active.qualification")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn(
        response.json["errors"][0]["description"],
        (
            "Can't update document because award of bid is not in one of statuses ('active',)",
            "Can't update document because award of bid is not in one of statuses ('active',)",
        ),
    )

    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
        {"data": document},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document because award of bid is not in one of statuses ('active',)",
    )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": document},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn(
        response.json["errors"][0]["description"],
        (
            "Can't add document because award of bid is not in one of statuses ('active',)",
            "Can't add document because award of bid is not in one of statuses ('active',)",
        ),
    )


def create_tender_bidder_document_json(self):
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
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}".format(self.tender_id, self.bid_id, doc_id, key), status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't view bid documents in current (active.tendering) tender status",
    )

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token
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
        "Can't view bid documents in current (active.tendering) tender status",
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
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

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
    self.assertIn(
        response.json["errors"][0]["description"],
        (
            "Can't add document because award of bid is not in one of statuses ('active',)",
            "Can't add document because award of bid is not in one of statuses ('active',)",
        ),
    )

    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("http://localhost/get/", response.json["data"]["url"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])

    response = self.app.get("/tenders/{}/bids/{}".format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, "200 OK")
    document = response.json["data"]["documents"][0]
    self.assertIn("http://localhost/get/", document["url"])
    self.assertIn("Signature=", document["url"])
    self.assertIn("KeyID=", document["url"])
    self.assertNotIn("Expires=", document["url"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token
        )
    )
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)


def put_tender_bidder_document_json(self):
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
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token
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
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}".format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    self.set_status("active.qualification")

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
    self.assertIn(
        response.json["errors"][0]["description"],
        (
            "Can't update document because award of bid is not in one of statuses ('active',)",
            "Can't update document because award of bid is not in one of statuses ('active',)",
        ),
    )

    response = self.app.get(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, doc_id, self.bid_token)
    )
    dos_service_ids = []
    for b in response.json["data"]["documents"]:
        self.assertIn("http://localhost/get/", b["url"])
        self.assertIn("Signature=", b["url"])
        self.assertIn("KeyID=", b["url"])
        start_len = len("http://localhost/get/")
        dos_service_ids.append(b["url"][start_len : start_len + 32])

    # check how data is stored in db
    tender = self.mongodb.tenders.get(self.tender_id)
    bid = tender["bids"][0]
    self.assertEqual(self.bid_id, bid["id"])

    for i, document in enumerate(bid["documents"][:-1]):  # exceptt proposal doc
        self.assertEqual(
            f"/tenders/{self.tender_id}/bids/{self.bid_id}/documents/{doc_id}?download={dos_service_ids[i]}",
            document["url"],
        )


def tender_bidder_confidential_document(self):
    request_data = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
        "confidentiality": "true",
    }

    # wrong value
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentiality",
                    "description": ["Value must be one of ['public', 'buyerOnly']."],
                }
            ],
        },
    )

    # empty confidentialityRationale
    request_data["confidentiality"] = "buyerOnly"
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            'status': 'error',
            'errors': [
                {
                    'description': ['confidentialityRationale is required'],
                    'location': 'body',
                    'name': 'confidentialityRationale',
                }
            ],
        },
    )

    # too short confidentialityRationale
    request_data["confidentialityRationale"] = "cuz"
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            'status': 'error',
            'errors': [
                {
                    'description': ['confidentialityRationale should contain at least 30 characters'],
                    'location': 'body',
                    'name': 'confidentialityRationale',
                }
            ],
        },
    )

    # success
    request_data["confidentialityRationale"] = "cuz" * 10
    response = self.app.post_json(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": request_data},
        status=201,
    )
    doc_data = response.json["data"]
    self.assertEqual(doc_data["confidentiality"], request_data["confidentiality"])
    self.assertEqual(doc_data["confidentialityRationale"], request_data["confidentialityRationale"])

    # patch back to short
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{self.bid_id}/documents/{doc_data['id']}?acc_token={self.bid_token}",
        {"data": {"confidentialityRationale": "cuz"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0],
        {
            'location': 'body',
            'name': 'confidentialityRationale',
            'description': ['confidentialityRationale should contain at least 30 characters'],
        },
    )

    # put back to short
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/bids/{self.bid_id}/documents/{doc_data['id']}?acc_token={self.bid_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                # "confidentiality": "buyerOnly",  # will be taken from the previous version
                "confidentialityRationale": "cuz",
            }
        },
        status=422,
    )
    try:
        self.assertEqual(
            response.json["errors"][0],
            {
                'location': 'body',
                'name': 'confidentialityRationale',
                'description': ['confidentialityRationale should contain at least 30 characters'],
            },
        )
    except AssertionError:  # "before refactoring" format
        self.assertEqual(
            response.json["errors"][0],
            {
                'location': 'body',
                'name': 'bids',
                'description': [
                    {
                        'documents': [
                            {
                                'confidentialityRationale': [
                                    'confidentialityRationale should contain at least 30 characters'
                                ]
                            }
                        ]
                    }
                ],
            },
        )
    self.activate_bid(self.tender_id, self.bid_id, self.bid_token)

    # switch to active.awarded
    tender = self.mongodb.tenders.get(self.tender_id)
    tender["status"] = "active.awarded"
    bid = [b for b in tender["bids"] if b["id"] == self.bid_id][0]
    tender["awards"] = [
        {
            "id": "0" * 32,
            "status": "active",
            "qualified": True,
            "eligible": True,
            "bid_id": self.bid_id,
            "date": get_now().isoformat(),
            "suppliers": bid["tenderers"],
        }
    ]
    self.mongodb.tenders.save(tender)

    # get list as tender owner
    response = self.app.get(
        "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, self.bid_id, self.tender_token)
    )
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0], doc_data)

    # get list as public
    response = self.app.get("/tenders/{}/bids/{}/documents".format(self.tender_id, self.bid_id))
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0], {k: v for k, v in doc_data.items() if k != "url"})

    # get directly as tender owner
    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.bid_id, doc_data["id"], self.tender_token
        )
    )
    self.assertEqual(response.json["data"], doc_data)

    # get directly as public
    response = self.app.get("/tenders/{}/bids/{}/documents/{}".format(self.tender_id, self.bid_id, doc_data["id"]))
    self.assertEqual(response.json["data"], {k: v for k, v in doc_data.items() if k != "url"})

    # download as tender owner
    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}&download=1".format(
            self.tender_id, self.bid_id, doc_data["id"], self.tender_token
        )
    )
    self.assertEqual(response.status_code, 302)
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    # download as tender public
    response = self.app.get(
        "/tenders/{}/bids/{}/documents/{}?download=1".format(self.tender_id, self.bid_id, doc_data["id"]), status=403
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "body", "name": "data", "description": "Document download forbidden."}],
        },
    )

    # trying to update confidentiality
    request_data["confidentiality"] = "public"
    expected_error = {
        'status': 'error',
        'errors': [
            {
                'description': "Can't update document confidentiality in current (active.awarded) tender status",
                'location': 'body',
                'name': 'data',
            }
        ],
    }
    response = self.app.put_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.bid_id, doc_data["id"], self.bid_token
        ),
        {"data": request_data},
        status=403,
    )
    self.assertEqual(response.json, expected_error)

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.bid_id, doc_data["id"], self.bid_token
        ),
        {"data": {"confidentiality": "public"}},
        status=403,
    )
    self.assertEqual(response.json, expected_error)


def create_bid_requirement_response(self):
    self.app.authorization = ("Basic", ("broker", ""))

    base_request_path = "/tenders/{}/bids/{}/requirement_responses".format(self.tender_id, self.bid_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.bid_token)

    valid_data = [
        {
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, self.tender_token),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(
        request_path,
        {"data": [{"description": "some description"}]},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {'location': 'body', 'name': 'requirement', 'description': ['This field is required.']},
        ],
    )

    del valid_data[0]["value"]
    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": "pending"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                "name": "requirementResponses",
                "description": [{"value": "Response required at least one of field [\"value\", \"values\"]"}],
            },
        ],
    )


def patch_bid_requirement_response(self):
    base_request_path = "/tenders/{}/bids/{}/requirement_responses".format(self.tender_id, self.bid_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.bid_token)

    valid_data = [
        {
            "title": "Requirement response",
            "description": "some description",
            "requirement": {
                "id": self.requirement_id,
                "title": self.requirement_title,
            },
            "value": True,
        }
    ]

    valid_data_2 = [
        {
            "title": "Requirement response 2",
            "description": "some description 2",
            "requirement": {
                "id": self.requirement_2_id,
                "title": self.requirement_2_title,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    response = self.app.post_json(request_path, {"data": valid_data_2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    base_request_path = "/tenders/{}/bids/{}/requirement_responses/{}".format(self.tender_id, self.bid_id, rr_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.bid_token)
    updated_data = {
        "title": "Rquirement response updated",
        "value": 100,
    }

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.patch_json(
        base_request_path,
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "{}?acc_token={}".format(base_request_path, self.tender_token),
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    self.app.authorization = auth
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['Must be either true or false.'],
                'location': 'body',
                'name': 'value',
            }
        ],
    )

    updated_data["value"] = True
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rr = response.json["data"]
    self.assertEqual(rr["title"], updated_data["title"])
    self.assertEqual(rr["value"], updated_data["value"])
    self.assertNotIn("evidences", rr)
    clean_requirement_responses([rr])

    response = self.app.patch_json(
        request_path,
        {
            "data": {
                "requirement": {
                    "id": self.requirement_2_id,
                    "title": self.requirement_2_title,
                },
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
                "name": "requirement",
                "description": "Requirement id should be uniq for all requirement responses",
            }
        ],
    )


def get_bid_requirement_response(self):
    base_request_path = "/tenders/{}/bids/{}/requirement_responses".format(self.tender_id, self.bid_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.bid_token)

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    valid_data = []
    for criterion in criteria:
        for req in criterion["requirementGroups"][0]["requirements"]:
            if criterion["source"] == "tenderer":
                valid_data.append(
                    {
                        "title": "Requirement response",
                        "description": "some description",
                        "requirement": {
                            "id": req["id"],
                            "title": req["title"],
                        },
                        "value": True,
                    }
                )
            elif criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE":
                guarantee_criterion = criterion

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": "pending"}},
    )

    response = self.app.get(base_request_path, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid in current (active.tendering) tender status"
    )

    self.set_status("active.qualification")

    response = self.app.get(base_request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rrs = response.json["data"]
    self.assertEqual(len(rrs), 10)

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            self.assertIn(k, rrs[i])
            self.assertEqual(v, rrs[i][k])

    response = self.app.get("{}/{}".format(base_request_path, rrs[0]["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data[0].items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])


def create_bid_requirement_response_evidence(self):
    base_request_path = "/tenders/{}/bids/{}/requirement_responses/{}/evidences".format(
        self.tender_id, self.bid_id, self.rr_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.bid_token)

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, self.tender_token),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])


def patch_bid_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.bid_id, self.rr_id, self.bid_token
        ),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    updated_data = {
        "title": "Updated title",
        "description": "Updated description",
    }

    response = self.app.patch_json(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.bid_id, self.rr_id, evidence_id, self.bid_token
        ),
        {"data": updated_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    self.assertEqual(evidence["title"], updated_data["title"])
    self.assertEqual(evidence["description"], updated_data["description"])


def get_bid_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.bid_id, self.rr_id, self.bid_token
        ),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    response = self.app.get(
        "/tenders/{}/bids/{}/requirement_responses".format(self.tender_id, self.bid_id),
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't view bid in current (active.tendering) tender status"
    )

    self.set_status("active.qualification")

    response = self.app.get(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences".format(self.tender_id, self.bid_id, self.rr_id)
    )

    evidences = response.json["data"]
    self.assertEqual(len(evidences), 1)

    for k, v in valid_data.items():
        self.assertIn(k, evidences[0])
        self.assertEqual(v, evidences[0][k])

    response = self.app.get(
        "/tenders/{}/bids/{}/requirement_responses/{}/evidences/{}".format(
            self.tender_id, self.bid_id, self.rr_id, evidence_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data.items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])


def bid_activate(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    next_status = "pending"

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    rrs = []
    criteria_ids = []

    guarantee_criterion = None

    for criterion in criteria:
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
                    }
                )
                if criterion["id"] not in criteria_ids:
                    criteria_ids.append(criterion["id"])
            elif criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE":
                guarantee_criterion = criterion

    rrs = rrs[1:]
    criteria_ids = criteria_ids[1:]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
        status=422,
    )

    if self.guarantee_criterion:
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("errors", response.json)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': [
                        "Responses are required for all criteria with source tenderer, "
                        f"failed for criteria {', '.join(criteria_ids + [guarantee_criterion['id']])}"
                    ],
                    'location': 'body',
                    'name': 'requirementResponses',
                }
            ],
        )

        guarantee_rr = [
            {
                "title": "Requirement response",
                "description": "some description",
                "requirement": {
                    "id": guarantee_criterion["requirementGroups"][0]["requirements"][0]["id"],
                    "title": guarantee_criterion["requirementGroups"][0]["requirements"][0]["title"],
                },
                "value": True,
            }
        ]
        response = self.app.post_json(
            "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(
                self.tender_id, self.bid_id, self.bid_token
            ),
            {"data": guarantee_rr},
        )
        self.assertEqual(response.status, "201 Created")

    else:

        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("errors", response.json)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': [
                        "Responses are required for all criteria with source tenderer, "
                        f"failed for criteria {', '.join(criteria_ids)}"
                    ],
                    'location': 'body',
                    'name': 'requirementResponses',
                }
            ],
        )

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": rrs[:-1]},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    "Responses are required for all requirements in a requirement group, "
                    f"failed for criteria {criteria_ids[-1]}"
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    another_rg_req = criteria[0]["requirementGroups"][1]["requirements"][0]
    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": [
                {
                    "title": "Requirement response",
                    "description": "some description",
                    "requirement": {
                        "id": another_rg_req["id"],
                        "title": another_rg_req["title"],
                    },
                    "value": True,
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    remove_rr_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    "Responses are allowed for only one group of requirements per criterion, "
                    f"failed for criteria {criteria[0]['id']}"
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    response = self.app.delete(
        "/tenders/{}/bids/{}/requirement_responses/{}?acc_token={}".format(
            self.tender_id, self.bid_id, remove_rr_id, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {
            "data": [
                {
                    "title": "Requirement response",
                    "description": "some description",
                    "requirement": {
                        "id": "0" * 32,
                        "title": "Requirement with invalid id title",
                    },
                    "value": True,
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    remove_rr_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [{'requirement': ['Requirement should be one of criteria requirements']}],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    response = self.app.delete(
        "/tenders/{}/bids/{}/requirement_responses/{}?acc_token={}".format(
            self.tender_id, self.bid_id, remove_rr_id, self.bid_token
        )
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": [rrs[-1]]},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def bid_activate_with_cancelled_tenderer_criterion(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    next_status = "pending"
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    rrs = []
    criteria_ids = []

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
                if criterion["id"] not in criteria_ids:
                    criteria_ids.append(criterion["id"])
    rrs = rrs[1:]

    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": rrs},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    'Responses are required for all criteria with source tenderer, '
                    f'failed for criteria {criteria[-1]["id"]}'
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )
    if not hasattr(self, "tender_auth"):
        self.tender_auth = self.app.authorization
    with change_auth(self.app, self.tender_auth) as app:
        criterion_to_cancel = criteria[-1]
        criterion_id = criterion_to_cancel["id"]
        rg_id = criterion_to_cancel["requirementGroups"][0]["id"]
        requirement_ids = [
            requirement["id"] for requirement in criterion_to_cancel["requirementGroups"][0]["requirements"]
        ]
        requirement_url = "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}"
        for requirement_id in requirement_ids:
            response = self.app.put_json(
                requirement_url.format(self.tender_id, criterion_id, rg_id, requirement_id, self.tender_token),
                {"data": {"status": "cancelled"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token),
        {"data": {"status": next_status}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def patch_bid_with_responses(self):
    base_request_path = "/tenders/{}/bids/{}".format(self.tender_id, self.bid_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.bid_token)

    valid_data = {
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": self.requirement_id,
            "title": self.requirement_title,
        },
        "value": True,
    }

    valid_data_1 = deepcopy(valid_data)
    valid_data_1["requirement"] = {
        "id": self.requirement_2_id,
        "title": self.requirement_2_title,
    }

    rrs = [valid_data, valid_data_1]
    clean_requirement_responses(rrs)
    # add
    response = self.app.patch_json(request_path, {"data": {"requirementResponses": rrs}})

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rrs = response.json["data"]["requirementResponses"]
    self.assertEqual(len(rrs), 2)

    clean_requirement_responses(rrs)

    valid_data["id"] = "2" * 32

    response = self.app.patch_json(
        request_path,
        {
            "data": {
                "requirementResponses": [rrs[1], valid_data],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rrs = response.json["data"]["requirementResponses"]
    self.assertEqual(len(rrs), 2)

    # patch first and third

    rrs[0]["title"] = "Requirement response 2"
    rrs[1]["title"] = "Requirement response 3"

    clean_requirement_responses(rrs)

    response = self.app.patch_json(request_path, {"data": {"requirementResponses": rrs}})

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rrs = response.json["data"]["requirementResponses"]
    self.assertEqual(rrs[0]["title"], "Requirement response 2")
    self.assertEqual(rrs[1]["title"], "Requirement response 3")


def bid_invalidation_after_requirement_put(self):
    next_status = "pending"
    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    rrs = []
    for criterion in criteria:
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

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], next_status)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    criteria_id = response.json["data"]["criteria"][-1]["id"]
    rg_id = response.json["data"]["criteria"][-1]["requirementGroups"][0]["id"]
    requirement_id = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]["id"]
    response = self.app.put_json(
        "/tenders/{}/criteria/{}/requirement_groups/{}/requirements/{}?acc_token={}".format(
            self.tender_id, criteria_id, rg_id, requirement_id, self.tender_token
        ),
        {"data": {"eligibleEvidences": [{"title": "1"}]}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "invalid")


def doc_date_modified(self):
    self.app.authorization = ("Basic", ("broker", ""))
    document = {
        "data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    }
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/bids/{self.bid_id}/documents?acc_token={self.bid_token}",
        document,
    )
    self.assertEqual(response.status, "201 Created")
    post_result = response.json["data"]
    self.assertEqual(post_result["datePublished"], post_result["dateModified"])

    # tender activation shouldn't change documents.dateModified
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/bids/{self.bid_id}?acc_token={self.bid_token}",
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")

    document = response.json["data"]["documents"][0]
    self.assertEqual(document["datePublished"], document["dateModified"])


def patch_tender_with_bids_lots_none(self):
    bid = self.test_bids_data[0].copy()
    lots = self.mongodb.tenders.get(self.tender_id).get("lots")

    set_bid_lotvalues(bid, lots)

    self.create_bid(self.tender_id, bid)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"lots": None}}, status=422
    )
    self.assertIn(
        {"location": "body", "name": "items", "description": [{"relatedLot": ["relatedLot should be one of lots"]}]},
        response.json["errors"],
    )


def bids_related_product(self):
    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    tender_item_1 = tender["items"][0]
    bid_data = self.test_bids_data[0].copy()
    if tender.get("lots"):
        set_bid_lotvalues(bid_data, self.initial_lots)

    related_product_id = "1" * 32
    bid_data["items"] = [
        {
            "quantity": 4,
            "description": "футляри до державних нагород",
            "id": tender_item_1["id"],
            # "unit": {"code": "KGM", "value": {"amount": 100, "currency": "UAH", "valueAddedTaxIncluded": True}},
            "product": related_product_id,
        },
    ]

    response_404 = Mock()
    response_404.status_code = 404

    with patch(
        "requests.get",
        Mock(return_value=response_404),
    ):
        response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data}, status=404)
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(
            response.json["errors"][0]["description"], f"Products {related_product_id} not found in catalouges."
        )

    response_200 = Mock()
    response_200.status_code = 200
    response_200.json = Mock(return_value={"data": {"id": related_product_id}})

    with patch(
        "requests.get",
        Mock(return_value=response_200),
    ):
        response = self.app.post_json(f"/tenders/{self.tender_id}/bids", {"data": bid_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["items"][0]["product"], related_product_id)
        bid_id = response.json["data"]["id"]
        bid_token = response.json["access"]["token"]

    items = bid_data["items"].copy()
    items[0]["quantity"] = 2

    with patch(
        "requests.get",
        Mock(return_value=response_404),
    ):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}", {"data": {"items": items}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["items"][0]["product"], related_product_id)

    related_product_id = "2" * 32
    items = bid_data["items"].copy()
    items[0]["product"] = related_product_id

    with patch(
        "requests.get",
        Mock(return_value=response_404),
    ):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid_id}?acc_token={bid_token}", {"data": {"items": items}}, status=404
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], f"Products {related_product_id} not found in catalouges."
        )
