# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.tender.belowthreshold.tests.base import test_cancellation
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.cancellation import activate_cancellation_after_2020_04_19


def update_patch_data(self, patch_data, key=None, start=0, interval=None):

    iterator = (
        list(range(self.min_bids_number))[start::interval] if start else list(range(self.min_bids_number))[::interval]
    )
    data = {
        "value": {"amount": 459, "currency": "UAH", "valueAddedTaxIncluded": True},
        "lotValues": [{"value": {"amount": 489, "currency": "UAH", "valueAddedTaxIncluded": True}}],
    }

    for x in iterator:
        patch_data["bids"].append({"id": self.initial_bids[x]["id"], key: data[key]})


# TenderAuctionResourceTest


def get_tender_auction_not_found(self):
    response = self.app.get("/tenders/some_id/auction", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/auction", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post_json("/tenders/some_id/auction", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    auction = response.json["data"]
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn("dateModified", auction)
    self.assertIn("minimalStep", auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]["value"]["amount"], self.initial_bids[0]["value"]["amount"])
    self.assertEqual(auction["bids"][1]["value"]["amount"], self.initial_bids[1]["value"]["amount"])
    # self.assertEqual(self.initial_data["auctionPeriod"]['startDate'], auction["auctionPeriod"]['startDate'])

    response = self.app.get("/tenders/{}/auction?opt_jsonp=callback".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get("/tenders/{}/auction?opt_pretty=1".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body)

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current (active.qualification) tender status",
    )


def post_tender_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True},
            }
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    update_patch_data(self, patch_data, key="value", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertNotEqual(tender["bids"][0]["value"]["amount"], self.initial_bids[0]["value"]["amount"])
    self.assertNotEqual(tender["bids"][-1]["value"]["amount"], self.initial_bids[-1]["value"]["amount"])
    self.assertEqual(tender["bids"][0]["value"]["amount"], patch_data["bids"][-1]["value"]["amount"])
    self.assertEqual(tender["bids"][-1]["value"]["amount"], patch_data["bids"][0]["value"]["amount"])
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], patch_data["bids"][0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], patch_data["bids"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


def patch_tender_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update auction urls in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.patch_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "auctionUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}".format(self.tender_id),
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.initial_bids[-1]["id"]
                ),
            }
        ],
    }

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    for x in list(range(self.min_bids_number))[-2::-1]:
        patch_data["bids"].append(
            {
                "id": self.initial_bids[x]["id"],
                "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.initial_bids[x]["id"]
                ),
            }
        )

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    for x, y in enumerate(list(range(self.min_bids_number))[::-1]):
        self.assertEqual(tender["bids"][x]["participationUrl"], patch_data["bids"][y]["participationUrl"])

    self.set_status("complete")

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update auction urls in current (complete) tender status"
    )


def post_tender_auction_document(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document in current ({}) tender status".format(
            self.forbidden_auction_document_create_actions_status
        ),
    )

    self.set_status("active.auction")

    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

    patch_data = {"bids": []}
    update_patch_data(self, patch_data, key="value", interval=-1)

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        upload_files=[("file", "name.doc", "content_with_names")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key2 = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    self.assertNotEqual(key, key2)

    self.set_status("complete")
    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


# TenderSameValueAuctionResourceTest


def post_tender_auction_not_changed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {"bids": self.initial_bids}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], self.initial_bids[0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])


def post_tender_auction_reversed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    now = get_now()
    patch_data = {
        "bids": [
            {"id": b["id"], "date": (now - timedelta(seconds=i)).isoformat(), "value": b["value"]}
            for i, b in enumerate(self.initial_bids)
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[-1]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], self.initial_bids[-1]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[-1]["tenderers"])


# TenderLotAuctionResourceTest


def get_tender_lot_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    auction = response.json["data"]
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn("dateModified", auction)
    self.assertIn("minimalStep", auction)
    self.assertIn("lots", auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(
        auction["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][0]["value"]["amount"], self.initial_bids[1]["lotValues"][0]["value"]["amount"]
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current (active.qualification) tender status",
    )


def post_tender_lot_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
    self.assertNotEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertNotEqual(
        tender["bids"][1]["lotValues"][0]["value"]["amount"], self.initial_bids[1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], patch_data["bids"][-1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][-1]["lotValues"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], patch_data["bids"][0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


def patch_tender_lot_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update auction urls in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    self.check_chronograph()

    response = self.app.patch_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "auctionUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}".format(self.tender_id),
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.initial_bids[1]["id"]
                ),
            }
        ],
    }

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"participationUrl": [u"url should be posted for each lot of bid"]}],
                u"location": u"body",
                u"name": u"bids",
            }
        ],
    )

    del patch_data["bids"][0]["participationUrl"]
    patch_data["bids"][0]["lotValues"] = [
        {
            "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                self.tender_id, self.initial_bids[0]["id"]
            )
        }
    ]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": ["url should be posted for each lot"], u"location": u"body", u"name": u"auctionUrl"}],
    )

    patch_data["lots"] = [{"auctionUrl": patch_data.pop("auctionUrl")}]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    for x in list(range(self.min_bids_number))[-2::-1]:
        patch_data["bids"].append(
            {
                "lotValues": [
                    {
                        "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                            self.tender_id, self.initial_bids[x]["id"]
                        )
                    }
                ]
            }
        )

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIsNone(response.json)
    for lot in self.initial_lots:
        response = self.app.patch_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["participationUrl"],
        patch_data["bids"][-1]["lotValues"][0]["participationUrl"],
    )
    self.assertEqual(
        tender["bids"][-1]["lotValues"][0]["participationUrl"],
        patch_data["bids"][0]["lotValues"][0]["participationUrl"],
    )
    self.assertEqual(tender["lots"][0]["auctionUrl"], patch_data["lots"][0]["auctionUrl"])

    self.set_status("complete")

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update auction urls in current (complete) tender status"
    )


def post_tender_lot_auction_document(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document in current ({}) tender status".format(
            self.forbidden_auction_document_create_actions_status
        ),
    )

    self.set_status("active.auction")

    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

    response = self.app.patch_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {"documentOf": "lot", "relatedItem": self.initial_lots[0]["id"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["documentOf"], "lot")
    self.assertEqual(response.json["data"]["relatedItem"], self.initial_lots[0]["id"])

    patch_data = {"bids": []}
    update_patch_data(self, patch_data, key="lotValues", interval=-1)

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        upload_files=[("file", "name.doc", "content_with_names")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key2 = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    self.assertNotEqual(key, key2)

    self.set_status("complete")
    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


# TenderMultipleLotAuctionResourceTest


def get_tender_lots_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    auction = response.json["data"]
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn("dateModified", auction)
    self.assertIn("minimalStep", auction)
    self.assertIn("lots", auction)
    self.assertIn("items", auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(
        auction["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][0]["value"]["amount"], self.initial_bids[1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][0]["lotValues"][1]["value"]["amount"], self.initial_bids[0]["lotValues"][1]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][1]["value"]["amount"], self.initial_bids[1]["lotValues"][1]["value"]["amount"]
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current (active.qualification) tender status",
    )


def post_tender_lots_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}],
    )

    for bid in patch_data["bids"]:
        bid["lotValues"] = [bid["lotValues"][0].copy() for i in self.initial_lots]

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.initial_bids[0]["lotValues"][0]["relatedLot"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"], [{u"lotValues": [u"bids don't allow duplicated proposals"]}]
    )

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.initial_bids[0]["lotValues"][1]["relatedLot"]
    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    self.assertNotEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertNotEqual(
        tender["bids"][1]["lotValues"][0]["value"]["amount"], self.initial_bids[1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], patch_data["bids"][-1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][-1]["lotValues"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], patch_data["bids"][0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


def patch_tender_lots_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update auction urls in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    self.check_chronograph()

    response = self.app.patch_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "auctionUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}".format(self.tender_id),
        "bids": [
            {
                "id": self.initial_bids[1]["id"],
                "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.initial_bids[1]["id"]
                ),
            }
        ],
    }

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"participationUrl": [u"url should be posted for each lot of bid"]}],
                u"location": u"body",
                u"name": u"bids",
            }
        ],
    )

    del patch_data["bids"][0]["participationUrl"]
    patch_data["bids"][0]["lotValues"] = [
        {
            "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                self.tender_id, self.initial_bids[0]["id"]
            )
        }
    ]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": ["url should be posted for each lot"], u"location": u"body", u"name": u"auctionUrl"}],
    )

    patch_data["lots"] = [{"auctionUrl": patch_data.pop("auctionUrl")}]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    patch_data["bids"].append(
        {
            "lotValues": [
                {
                    "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                        self.tender_id, self.initial_bids[0]["id"]
                    )
                }
            ]
        }
    )

    patch_data["bids"][1]["id"] = "some_id"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][1]["id"] = self.initial_bids[0]["id"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], u"Number of lots did not match the number of tender lots"
    )

    patch_data["lots"] = [patch_data["lots"][0].copy() for i in self.initial_lots]
    patch_data["lots"][1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], u"Auction lots should be identical to the tender lots")

    patch_data["lots"][1]["id"] = self.initial_lots[1]["id"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}],
    )

    for bid in patch_data["bids"]:
        bid["lotValues"] = [bid["lotValues"][0].copy() for i in self.initial_lots]

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.initial_bids[0]["lotValues"][0]["relatedLot"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"], [{u"lotValues": [u"bids don't allow duplicated proposals"]}]
    )

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.initial_bids[0]["lotValues"][1]["relatedLot"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIsNone(response.json)

    for lot in self.initial_lots:
        response = self.app.patch_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["participationUrl"], patch_data["bids"][1]["lotValues"][0]["participationUrl"]
    )
    self.assertEqual(
        tender["bids"][1]["lotValues"][0]["participationUrl"], patch_data["bids"][0]["lotValues"][0]["participationUrl"]
    )
    self.assertEqual(tender["lots"][0]["auctionUrl"], patch_data["lots"][0]["auctionUrl"])

    self.app.authorization = ("Basic", ("token", ""))
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    if RELEASE_2020_04_19 > get_now():
        response = self.app.post_json("/tenders/{}/cancellations".format(self.tender_id), {"data": cancellation})
        self.assertEqual(response.status, "201 Created")

        cancellation_id = response.json["data"]["id"]

        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.patch_json(
            "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]), {"data": patch_data},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can update auction urls only in active lot status")


def post_tender_lots_auction_document(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document in current ({}) tender status".format(
            self.forbidden_auction_document_create_actions_status
        ),
    )

    self.set_status("active.auction")

    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

    response = self.app.patch_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {"documentOf": "lot", "relatedItem": self.initial_lots[0]["id"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["documentOf"], "lot")
    self.assertEqual(response.json["data"]["relatedItem"], self.initial_lots[0]["id"])

    patch_data = {"bids": []}
    for x in list(range(self.min_bids_number))[::-1]:
        patch_data["bids"].append(
            {
                "id": self.initial_bids[x]["id"],
                "lotValues": [
                    {"value": {"amount": 409 + x * 10, "currency": "UAH", "valueAddedTaxIncluded": True}}
                    for i in self.initial_lots
                ],
            }
        )

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        upload_files=[("file", "name.doc", "content_with_names")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key2 = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    self.assertNotEqual(key, key2)

    self.set_status("complete")
    response = self.app.post(
        "/tenders/{}/documents".format(self.tender_id), upload_files=[("file", "name.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


# TenderFeaturesAuctionResourceTest
def get_tender_auction_feature(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    auction = response.json["data"]
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn("dateModified", auction)
    self.assertIn("minimalStep", auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]["value"]["amount"], self.initial_bids[0]["value"]["amount"])
    self.assertEqual(auction["bids"][1]["value"]["amount"], self.initial_bids[1]["value"]["amount"])
    self.assertIn("features", auction)
    self.assertIn("parameters", auction["bids"][0])


def post_tender_auction_feature(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update auction urls in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "value": {"amount": 459, "currency": "UAH", "valueAddedTaxIncluded": True},
            }
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    update_patch_data(self, patch_data, key="value", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")
    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("features", tender)
    self.assertIn("parameters", tender["bids"][0])
    self.assertEqual(tender["bids"][0]["value"]["amount"], patch_data["bids"][-1]["value"]["amount"])
    self.assertEqual(tender["bids"][-1]["value"]["amount"], patch_data["bids"][0]["value"]["amount"])

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    # bids have same amount, but bid with better parameters awarded
    self.assertEqual(tender["awards"][0]["bid_id"], tender["bids"][1]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], tender["bids"][1]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[1]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


# TenderFeaturesLotAuctionResourceTest
def get_tender_lot_auction_features(self):
    self.app.authorization = ("Basic", ("auction", ""))

    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    auction = response.json["data"]
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn("dateModified", auction)
    self.assertIn("minimalStep", auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertIn("lots", auction)
    self.assertEqual(
        auction["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][0]["value"]["amount"], self.initial_bids[1]["lotValues"][0]["value"]["amount"]
    )

    self.assertEqual(auction["bids"][0]["parameters"][0]["code"], self.initial_bids[0]["parameters"][0]["code"])
    self.assertEqual(auction["bids"][0]["parameters"][0]["value"], self.initial_bids[0]["parameters"][0]["value"])
    self.assertEqual(auction["bids"][0]["parameters"][1]["code"], self.initial_bids[0]["parameters"][1]["code"])
    self.assertEqual(auction["bids"][0]["parameters"][1]["value"], self.initial_bids[0]["parameters"][1]["value"])
    self.assertIn("features", auction)
    self.assertIn("parameters", auction["bids"][0])


def post_tender_lot_auction_features(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
    self.assertIn("features", tender)
    self.assertIn("parameters", tender["bids"][0])
    self.assertNotEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertNotEqual(
        tender["bids"][-1]["lotValues"][0]["value"]["amount"], self.initial_bids[-1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], patch_data["bids"][-1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][-1]["lotValues"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], patch_data["bids"][0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


# TenderFeaturesMultilotAuctionResourceTest
def get_tender_lots_auction_features(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    auction = response.json["data"]
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn("dateModified", auction)
    self.assertIn("minimalStep", auction)
    self.assertIn("lots", auction)
    self.assertIn("items", auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(
        auction["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][0]["value"]["amount"], self.initial_bids[1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][0]["lotValues"][1]["value"]["amount"], self.initial_bids[0]["lotValues"][1]["value"]["amount"]
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][1]["value"]["amount"], self.initial_bids[1]["lotValues"][1]["value"]["amount"]
    )

    self.assertEqual(auction["bids"][0]["parameters"][0]["code"], self.initial_bids[0]["parameters"][0]["code"])
    self.assertEqual(auction["bids"][0]["parameters"][0]["value"], self.initial_bids[0]["parameters"][0]["value"])
    self.assertEqual(auction["bids"][0]["parameters"][1]["code"], self.initial_bids[0]["parameters"][1]["code"])
    self.assertEqual(auction["bids"][0]["parameters"][1]["value"], self.initial_bids[0]["parameters"][1]["value"])
    self.assertIn("features", auction)
    self.assertIn("parameters", auction["bids"][0])

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/auction".format(self.tender_id), status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't get auction info in current (active.qualification) tender status",
    )


def post_tender_lots_auction_features(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"invalid_field": u"Rogue field"}, u"location": u"body", u"name": u"bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {u"id": [u"Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}],
    )

    for bid in patch_data["bids"]:
        bid["lotValues"] = [bid["lotValues"][0].copy() for i in self.initial_lots]

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.initial_bids[0]["lotValues"][0]["relatedLot"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"], [{u"lotValues": [u"bids don't allow duplicated proposals"]}]
    )

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.initial_bids[0]["lotValues"][1]["relatedLot"]

    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
    self.assertIn("features", tender)
    self.assertIn("parameters", tender["bids"][0])
    self.assertNotEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"]
    )
    self.assertNotEqual(
        tender["bids"][-1]["lotValues"][0]["value"]["amount"], self.initial_bids[-1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], patch_data["bids"][-1]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][-1]["lotValues"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], patch_data["bids"][0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )
