from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.core.tests.utils import activate_contract
from openprocurement.tender.open.tests.below_threshold.base import (
    test_tender_below_cancellation,
    test_tender_below_supplier,
)


def add_single_lot(self, tender_id, owner_token):
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot = response.json["data"]

    items = deepcopy(self.initial_data["items"])
    items[0]["relatedLot"] = lot["id"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    return lot


def add_two_lots(self, tender_id, owner_token):
    lots = []
    for _ in range(2):
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])

    item = deepcopy(self.initial_data["items"][0])
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [item for _ in lots]}},
    )
    items = deepcopy(response.json["data"]["items"])
    for n, lot_id in enumerate(lots):
        items[n]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    return lots


def switch_to_auction(self):
    self.time_shift("active.auction")
    return self.check_chronograph()


def post_auction_results(self, tender_id, lot_id, auction_bids_data):
    self.app.authorization = ("Basic", ("auction", ""))
    return self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": lot["relatedLot"]} for lot in b.get("lotValues", "")]}
                    for b in auction_bids_data
                ]
            }
        },
    )


def activate_award_for_lot(self, tender_id, owner_token, lot_id=None):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    award_id = [
        i["id"] for i in response.json["data"] if i["status"] == "pending" and (lot_id is None or i["lotID"] == lot_id)
    ][0]
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    response = self.app.get("/tenders/{}".format(tender_id))
    return response.json["data"]["contracts"][-1]["id"]


def expire_award_complaint_periods(self, tender_id):
    tender = self.mongodb.tenders.get(tender_id)
    now = (get_now() - timedelta(seconds=1)).isoformat()
    for award in tender.get("awards", []):
        award["complaintPeriod"] = {"startDate": now, "endDate": now}
    self.mongodb.tenders.save(tender)


def patch_tender_bidder(self):
    lot_id = self.initial_lots[0]["id"]
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"value": {"amountPercentage": 50}, "relatedLot": lot_id}]
    del bid_data["value"]

    bidder, bid_token = self.create_bid(self.tender_id, bid_data)
    lot = bidder["lotValues"][0]
    lot_values = bidder["lotValues"]

    tenderer = deepcopy(test_tender_below_supplier)
    tenderer["name"] = "Державне управління управлінням справами"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bidder["id"], bid_token)
    doc_id = response.json["data"]["documents"][-1]["id"]
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {
            "data": {
                "lotValues": [{**lot_values[0], "value": {"amountPercentage": 50}, "relatedLot": lot_id}],
                "tenderers": self.test_bids_data[0]["tenderers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bidder["id"], bid_token, doc_id)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"lotValues": [{**lot_values[0], "value": {"amountPercentage": 39}, "relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.activate_bid(self.tender_id, bidder["id"], bid_token, doc_id)
    self.assertEqual(response.json["data"]["lotValues"][0]["value"]["amountPercentage"], 39)
    self.assertNotEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])

    self.time_shift("active.auction")
    self.check_chronograph()

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {
            "data": {
                "lotValues": [{**lot_values[0], "value": {"amountPercentage": 50}, "relatedLot": lot_id}],
                "status": "active",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update bid in current (unsuccessful) tender status"
    )


def one_lot_1bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

    lot = add_single_lot(self, tender_id, owner_token)
    self.set_initial_status(tender_response)

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot["id"]}]

    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")

    switch_to_auction(self)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

    lot = add_single_lot(self, tender_id, owner_token)
    lot_id = lot["id"]
    self.initial_lots = [lot]
    self.set_initial_status(tender_response)

    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]
    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]

    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id}]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")

    response = switch_to_auction(self)
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "lots": [
                    {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
                ],
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

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    post_auction_results(self, tender_id, lot_id, auction_bids_data)

    contract_id = activate_award_for_lot(self, tender_id, owner_token)

    self.time_shift("complete")
    self.check_chronograph()
    expire_award_complaint_periods(self, tender_id)

    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_3bid_1del(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

    lot = add_single_lot(self, tender_id, owner_token)
    lot_id = lot["id"]
    self.initial_lots = [lot]
    self.set_initial_status(tender_response)

    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]
    for _ in range(3):
        bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
        bids.append((bid["id"], bid_token))

    response = self.app.delete("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bids[2][0], bids[2][1]))
    self.assertEqual(response.status, "200 OK")

    response = switch_to_auction(self)
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id),
        {
            "data": {
                "lots": [
                    {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
                ],
                "bids": [
                    (
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"participationUrl": "https://tender.auction.url/for_bid/{}".format(b["id"])}
                                for _ in b.get("lotValues", "")
                            ],
                        }
                        if b.get("status", "active") == "active"
                        else {}
                    )
                    for b in auction_bids_data
                ],
            }
        },
    )

    self.app.authorization = ("Basic", ("broker", ""))
    bid_id, bid1_token = bids[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid1_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    post_auction_results(self, tender_id, lot_id, auction_bids_data)

    contract_id = activate_award_for_lot(self, tender_id, owner_token)

    self.time_shift("complete")
    self.check_chronograph()
    expire_award_complaint_periods(self, tender_id)

    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_2bid_1can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

    lots = add_two_lots(self, tender_id, owner_token)
    self.set_initial_status(tender_response)

    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    for i in range(self.min_bids_number):
        bid_data.update(
            {
                "tenderers": self.test_bids_data[i]["tenderers"],
                "lotValues": [{"value": self.test_bids_data[i]["value"], "relatedLot": lot_id} for lot_id in lots],
            }
        )
        self.create_bid(tender_id, bid_data, "pending")

    if RELEASE_2020_04_19 < get_now():
        self.set_complaint_period_end()

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lots[0],
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.status, "200 OK")
    lot_statuses = {lot["id"]: lot["status"] for lot in response.json["data"]["lots"]}
    self.assertEqual(lot_statuses[lots[0]], "cancelled")
    self.assertEqual(lot_statuses[lots[1]], "active")

    response = switch_to_auction(self)
    self.assertEqual(response.json["data"]["status"], "active.auction")


def two_lot_2bid_2win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

    lots = add_two_lots(self, tender_id, owner_token)
    self.initial_lots = lots
    self.set_initial_status(tender_response)

    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id} for lot_id in lots]
    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")

    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id} for lot_id in lots]
    self.app.authorization = ("Basic", ("broker", ""))
    _, bid2_token = self.create_bid(tender_id, bid_data, "pending")

    response = switch_to_auction(self)
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in lots:
        response = self.app.patch_json(
            "/tenders/{}/auction/{}".format(tender_id, lot_id),
            {
                "data": {
                    "lots": [
                        {"id": i["id"], "auctionUrl": "https://tender.auction.url"}
                        for i in response.json["data"]["lots"]
                    ],
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
        post_auction_results(self, tender_id, lot_id, auction_bids_data)

    contract_id = activate_award_for_lot(self, tender_id, owner_token, lots[0])
    expire_award_complaint_periods(self, tender_id)
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lots[1]][0]
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )

    contract_id = activate_award_for_lot(self, tender_id, owner_token, lots[1])

    self.set_status("complete", {"status": "active.awarded"})
    expire_award_complaint_periods(self, tender_id)

    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid2_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all(i["status"] == "complete" for i in response.json["data"]["lots"]))
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_3bid_1win_bug(self):
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender_response = response.json

    lots = add_two_lots(self, tender_id, owner_token)
    self.initial_lots = lots
    self.set_initial_status(tender_response)

    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id} for lot_id in lots]
    _, bid1_token = self.create_bid(tender_id, bid_data, "pending")

    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    bid_data["lotValues"] = [{"value": self.test_bids_data[1]["value"], "relatedLot": lot_id} for lot_id in lots]
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")

    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, deepcopy(bid_data), "pending")

    response = switch_to_auction(self)
    self.assertEqual(response.json["data"]["status"], "active.auction")

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in lots:
        response = self.app.patch_json(
            "/tenders/{}/auction/{}".format(tender_id, lot_id),
            {
                "data": {
                    "lots": [
                        {"id": i["id"], "auctionUrl": "https://tender.auction.url"}
                        for i in response.json["data"]["lots"]
                    ],
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
        post_auction_results(self, tender_id, lot_id, auction_bids_data)

    contract_id = activate_award_for_lot(self, tender_id, owner_token, lots[0])
    expire_award_complaint_periods(self, tender_id)
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)

    while True:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        pending = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lots[1]]
        if not pending:
            break
        award_id = pending[0]
        self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
        )

    self.set_status("complete", {"status": "active.awarded"})
    expire_award_complaint_periods(self, tender_id)
    self.check_chronograph()

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual({i["status"] for i in response.json["data"]["lots"]}, {"complete", "unsuccessful"})
    self.assertEqual(response.json["data"]["status"], "complete")
