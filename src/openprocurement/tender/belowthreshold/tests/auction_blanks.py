# -*- coding: utf-8 -*-
from datetime import timedelta
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_draft_claim,
)


def update_patch_data(self, patch_data, key=None, start=0, interval=None, with_weighted_value=False):
    if start:
        iterator = list(range(self.min_bids_number))[start::interval]
    else:
        iterator = list(range(self.min_bids_number))[::interval]

    bid_patch_data_value = {
        "value": {
            "amount": 489,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    }

    if with_weighted_value:
        bid_patch_data_value.update({
            "weightedValue": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        })

    for x in iterator:
        bid_patch_data = {"id": self.initial_bids[x]["id"]}
        if key == "value":
            bid_patch_data.update(bid_patch_data_value)
        elif key == "lotValues":
            bid_patch_data.update({"lotValues": [bid_patch_data_value]})
        patch_data["bids"].append(bid_patch_data)


# TenderAuctionResourceTest


def get_tender_auction_not_found(self):
    response = self.app.get("/tenders/some_id/auction", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/auction", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.post_json("/tenders/some_id/auction", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
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
    self.assertIn('callback({"data": {"', response.body.decode())  # PY3_TRICK

    response = self.app.get("/tenders/{}/auction?opt_pretty=1".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())

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
        [{"description": {"invalid_field": "Rogue field"}, "location": "body", "name": "bids"}],
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
        response.json["errors"][0]["description"],
        ["Number of auction results did not match the number of tender bids"]
    )

    update_patch_data(self, patch_data, key="value", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {"id": ["Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction bids should be identical to the tender bids"])

    patch_data["bids"] = [{"value": {"amount": n}}
                          for n, b in enumerate(self.initial_bids)]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    for n, b in enumerate(tender["bids"]):
        self.assertEqual(b["value"]["amount"], n)

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], 0)
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


def post_tender_auction_weighted_value(self):
    if self.tender_class.procurementMethodType.default not in ("openua", "openeu", "simple.defense"):
        self.skipTest("weightedValue is not implemented")

    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")

    patch_data = {"bids": []}
    update_patch_data(self, patch_data, key="value", start=0, interval=1, with_weighted_value=True)

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    first_bid_weighted_amount = tender["bids"][0]["weightedValue"]["amount"]
    last_bid_weighted_amount = tender["bids"][-1]["weightedValue"]["amount"]

    first_bid_patch_weighted_amount = patch_data["bids"][0]["weightedValue"]["amount"]
    last_bid_patch_weighted_amount = patch_data["bids"][-1]["weightedValue"]["amount"]

    self.assertEqual(first_bid_weighted_amount, last_bid_patch_weighted_amount)
    self.assertEqual(last_bid_weighted_amount, first_bid_patch_weighted_amount)

    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["weightedValue"]["amount"], first_bid_patch_weighted_amount)


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
        [{"description": {"invalid_field": "Rogue field"}, "location": "body", "name": "bids"}],
    )

    patch_data = {
        "auctionUrl": "http://auction-sandbox.openprocurement.org/tenders/{}".format(self.tender_id),
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "participationUrl": "http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.initial_bids[-1]["id"]
                ),
            }
        ],
    }

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], ["Number of bids did not match the number of tender bids"]
    )

    for x in list(range(self.min_bids_number))[-2::-1]:
        patch_data["bids"].append(
            {
                "id": self.initial_bids[x]["id"],
                "participationUrl": "http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.initial_bids[x]["id"]
                ),
            }
        )

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {"id": ["Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction bids should be identical to the tender bids"])

    patch_data["bids"] = [{"participationUrl": f"http://auction.prozorro.gov.ua/{b['id']}"}
                          for b in self.initial_bids]
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    for b in tender["bids"]:
        self.assertEqual(b["participationUrl"], f"http://auction.prozorro.gov.ua/{b['id']}")

    self.set_status("complete")

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update auction urls in current (complete) tender status"
    )


def post_tender_auction_document(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403
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

    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    url = response.json["data"]["url"]

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id),
                                  {"data": {"bids": [{"id": b["id"]} for b in self.initial_bids]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    response = self.app.put_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotEqual(url, response.json["data"]["url"])

    self.set_status("complete")
    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


# TenderSameValueAuctionResourceTest


def post_tender_auction_not_changed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id),
                                  {"data": {"bids": [
                                      {"id": b["id"], "value": b["value"]}
                                      for b in self.initial_bids]}})
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


def post_tender_lot_auction_weighted_value(self):
    if self.tender_class.procurementMethodType.default not in ("openua", "openeu", "simple.defense"):
        self.skipTest("weightedValue is not implemented")

    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{
                    "value": {
                        "amount": 409,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": True
                    },
                    "weightedValue": {
                        "amount": 399,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": True
                    },
                }],
            }
        ]
    }

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1, with_weighted_value=True)

    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    first_bid_weighted_amount = tender["bids"][0]["lotValues"][0]["weightedValue"]["amount"]
    last_bid_weighted_amount = tender["bids"][-1]["lotValues"][0]["weightedValue"]["amount"]

    first_bid_patch_weighted_amount = patch_data["bids"][0]["lotValues"][0]["weightedValue"]["amount"]
    last_bid_patch_weighted_amount = patch_data["bids"][-1]["lotValues"][0]["weightedValue"]["amount"]

    self.assertEqual(first_bid_weighted_amount, last_bid_patch_weighted_amount)
    self.assertEqual(last_bid_weighted_amount, first_bid_patch_weighted_amount)

    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["weightedValue"]["amount"], first_bid_patch_weighted_amount)


def post_tender_lot_auction_document(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403
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

    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    url = response.json["data"]["url"]

    response = self.app.patch_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {"documentOf": "lot", "relatedItem": self.initial_lots[0]["id"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["documentOf"], "lot")
    self.assertEqual(response.json["data"]["relatedItem"], self.initial_lots[0]["id"])

    patch_data = {"bids": [{"id": b["id"], "lotValues": [{"relatedLot": l["id"]} for l in self.initial_lots]}
                           for b in self.initial_bids]}

    lot_id = self.initial_lots[0]["id"]
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key2 = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotEqual(url, response.json["data"]["url"])

    self.set_status("complete")
    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403
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
    lot_id = self.initial_lots[0]["id"]
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    if self.initial_data["procurementMethodType"] in (
        "belowThreshold",
    ):
        self.set_status("active.enquiries")

    # should not affect changing status
    if self.initial_data["procurementMethodType"] in (
        "belowThreshold",
        "simple.defense",
    ):
        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.post_json(
                f"/tenders/{self.tender_id}/complaints",
                {"data": test_tender_below_draft_claim},
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
        [{"description": {"invalid_field": "Rogue field"}, "location": "body", "name": "bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Number of auction results did not match the number of tender bids"]
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {"id": ["Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction bids should be identical to the tender bids"])

    # patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    patch_data["bids"] = [{"lotValues": [{}, {}, {}]} for b in self.initial_bids]
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Number of lots of auction results did not match the number of tender lots"],
    )

    patch_data["bids"] = [{"lotValues": [{"relatedLot": lot_id}, {"relatedLot": lot_id}]}
                          for b in self.initial_bids]

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"],
        ['Auction bid.lotValues should be identical to the tender bid.lotValues']
    )

    num = 0
    for lot in self.initial_lots:
        patch_data["bids"] = [{"lotValues": [{"value": {"amount": 10 ** num}} for _ in b["lotValues"]]}
                              for b in self.initial_bids]
        num += 1

        response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot['id']}", {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    for b in tender["bids"]:
        self.assertEqual(b["lotValues"][0]["value"]["amount"], 1)
        self.assertEqual(b["lotValues"][1]["value"]["amount"], 10)

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], 1)
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


def post_tender_lots_auction_weighted_value(self):
    if self.tender_class.procurementMethodType.default not in ("openua", "openeu", "simple.defense"):
        self.skipTest("weightedValue is not implemented")

    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")

    patch_data = {"bids": []}
    update_patch_data(self, patch_data, key="lotValues", with_weighted_value=True)

    for bid in patch_data["bids"]:
        bid["lotValues"] = [bid["lotValues"][0].copy() for i in self.initial_lots]

    for lot in self.initial_lots:
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]),
            {"data": patch_data}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    first_bid_weighted_amount = tender["bids"][0]["lotValues"][0]["weightedValue"]["amount"]
    last_bid_weighted_amount = tender["bids"][-1]["lotValues"][0]["weightedValue"]["amount"]

    first_bid_patch_weighted_amount = patch_data["bids"][0]["lotValues"][0]["weightedValue"]["amount"]
    last_bid_patch_weighted_amount = patch_data["bids"][-1]["lotValues"][0]["weightedValue"]["amount"]

    self.assertEqual(first_bid_weighted_amount, last_bid_patch_weighted_amount)
    self.assertEqual(last_bid_weighted_amount, first_bid_patch_weighted_amount)

    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["weightedValue"]["amount"], first_bid_patch_weighted_amount)


def patch_tender_lots_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    lot_id = self.initial_lots[0]["id"]
    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update auction urls in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    self.check_chronograph()

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/auction/{lot_id}",
        {"data": {"bids": [{"invalid_field": "invalid_value"}]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"invalid_field": "Rogue field"}, "location": "body", "name": "bids"}],
    )

    patch_data = {
        "auctionUrl": "http://auction-sandbox.openprocurement.org/tenders/{}".format(self.tender_id),
        "bids": [
            {
                "id": b["id"],
                "participationUrl": "http://auction-sandbox.openprocurement.org/tenders/id",
            }
            for b in self.initial_bids
        ],
    }

    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"participationUrl": ["url should be posted for each lot of bid"]}],
                "location": "body",
                "name": "bids",
            }
        ],
    )

    del patch_data["bids"][0]["participationUrl"]
    patch_data["bids"][0]["lotValues"] = [
        {
            "participationUrl": "http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                self.tender_id, self.initial_bids[0]["id"]
            )
        }
    ]

    patch_data = {
        "lots": [{"auctionUrl": "http://auction.openprocurement.org/tenders/id"}],
        "bids": [
            {"lotValues": [{"participationUrl": "http://auction.openprocurement.org/id"} for v in b["lotValues"]]}
            for b in self.initial_bids
        ],
    }
    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{'location': 'body', 'name': 'lots',
          'description': ['Number of lots did not match the number of tender lots']}]
    )

    patch_data["lots"].append({})

    patch_data["bids"][1]["id"] = "some_id"

    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {"id": ["Hash value is wrong length."]})

    patch_data["bids"][1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction bids should be identical to the tender bids"])

    patch_data["bids"][1]["id"] = self.initial_bids[0]["id"]
    patch_data["lots"][1]["id"] = "00000000000000000000000000000000"
    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction lots should be identical to the tender lots"])

    patch_data = {
        "lots": [{"auctionUrl": "http://auction.openprocurement.org/tenders/id"}, {}],
        "bids": [
            {"lotValues": [{"participationUrl": "http://auction.openprocurement.org/id"}, {}, {}]}
            for b in self.initial_bids
        ],
    }
    response = self.app.patch_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Number of lots of auction results did not match the number of tender lots"],
    )

    for bid in patch_data["bids"]:
        bid["lotValues"] = [bid["lotValues"][0].copy() for i in self.initial_lots]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "bids", "description": [
            {"participationUrl": ["url should be posted for each lot of bid"]}]}
    )

    for lot in self.initial_lots:
        patch_data = {
            "lots": [
                {"auctionUrl": f"http://auction.prozorro.gov.ua/{l['id']}"} if l["id"] == lot["id"] else {}
                for l in self.initial_lots
            ],
            "bids": [
                {"lotValues": [
                    {"participationUrl": f"http://auction.prozorro.gov.ua/{v['relatedLot']}"}
                    if v["relatedLot"] == lot["id"] else {}
                    for v in b["lotValues"]
                ]}
                for b in self.initial_bids
            ]
        }
        response = self.app.patch_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        resp = response.json["data"]

    for bid in resp["bids"]:
        for l in bid["lotValues"]:
            self.assertEqual(l["participationUrl"], f"http://auction.prozorro.gov.ua/{l['relatedLot']}")
    for l in resp["lots"]:
        self.assertEqual(l["auctionUrl"], f"http://auction.prozorro.gov.ua/{l['id']}")

    self.app.authorization = ("Basic", ("token", ""))
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    if RELEASE_2020_04_19 > get_now():
        response = self.app.post_json("/tenders/{}/cancellations".format(self.tender_id), {"data": cancellation})
        self.assertEqual(response.status, "201 Created")

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
    lot_id = self.initial_lots[0]["id"]
    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403
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

    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    url = response.json["data"]["url"]

    response = self.app.patch_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {"documentOf": "lot", "relatedItem": self.initial_lots[0]["id"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["documentOf"], "lot")
    self.assertEqual(response.json["data"]["relatedItem"], self.initial_lots[0]["id"])

    patch_data = {"bids": [
        {
            "lotValues": [
                {"relatedLot": i["id"]}
                for i in self.initial_lots
            ],
        } for b in self.initial_bids
    ]}

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.put_json(
        "/tenders/{}/documents/{}".format(self.tender_id, doc_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotEqual(url, response.json["data"]["url"])

    self.set_status("complete")
    response = self.app.post_json(
        "/tenders/{}/documents".format(self.tender_id),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403
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
        [{"description": {"invalid_field": "Rogue field"}, "location": "body", "name": "bids"}],
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
        response.json["errors"][0]["description"], ["Number of auction results did not match the number of tender bids"]
    )

    update_patch_data(self, patch_data, key="value", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {"id": ["Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction bids should be identical to the tender bids"])

    patch_data = {"bids": [
        {"value": {"amount": 11111}},
        {"value": {"amount": 2222}},
    ]}
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("features", tender)
    self.assertIn("parameters", tender["bids"][0])
    self.assertEqual(tender["bids"][0]["value"]["amount"], patch_data["bids"][0]["value"]["amount"])
    self.assertEqual(tender["bids"][1]["value"]["amount"], patch_data["bids"][1]["value"]["amount"])

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
    lot_id = self.initial_lots[0]["id"]
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": {}}, status=403)
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
        [{"description": {"invalid_field": "Rogue field"}, "location": "body", "name": "bids"}],
    )

    patch_data = {
        "bids": [
            {
                "id": self.initial_bids[-1]["id"],
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], ["Number of auction results did not match the number of tender bids"]
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"][-1]["id"] = "some_id"

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], {"id": ["Hash value is wrong length."]})

    patch_data["bids"][-1]["id"] = "00000000000000000000000000000000"

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], ["Auction bids should be identical to the tender bids"])

    patch_data = {
        "bids": [
            {"lotValues": [{}, {}, {}]}
            for b in self.initial_bids
        ]
    }
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Number of lots of auction results did not match the number of tender lots"],
    )

    patch_data = {
        "bids": [
            {"lotValues": [
                {"relatedLot": b["lotValues"][0]["relatedLot"]},
                {"relatedLot": b["lotValues"][0]["relatedLot"]},
            ]}
            for b in self.initial_bids
        ]
    }
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Auction bid.lotValues should be identical to the tender bid.lotValues"]
    )

    patch_data = {
        "bids": [
            {"lotValues": [
                {"value": {"amount": 1 + n}}
                for n, l in enumerate(b["lotValues"])
            ]}
            for b in self.initial_bids
        ]
    }
    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
    self.assertIn("features", tender)
    self.assertIn("parameters", tender["bids"][0])
    for b in tender["bids"]:
        self.assertEqual(b["lotValues"][0]["value"]["amount"], 1)
        self.assertEqual(b["lotValues"][1]["value"]["amount"], 2)
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[1]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )
