# -*- coding: utf-8 -*-
from copy import deepcopy
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import activate_cancellation_with_complaints_after_2020_04_19
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_cancellation


@patch("openprocurement.tender.core.models.TWO_PHASE_COMMIT_FROM", get_now() + timedelta(days=1))
def create_tender_bidder_invalid(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.pop("lotValues", None)
    request_path = "/tenders/{}/bids".format(self.tender_id)
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "lotValues"}],
    )

    bid_data["lotValues"] = [{"relatedLot": "0" * 32}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    # Field 'value' doesn't exists on first stage
    bid_data["lotValues"] = [{"value": {"amount": 5000000}, "relatedLot": self.initial_lots[0]["id"]}]

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422
    )
    self.assertEqual(
        response.json,
        {"status": "error", "errors": [
            {"location": "body", "name": "lotValues", "description": {"value": "Rogue field"}}]})


def patch_tender_bidder(self):
    lot_id = self.initial_lots[0]["id"]
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder, bid_token = self.create_bid(self.tender_id, bid_data)
    lot = bidder["lotValues"][0]

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"tenderers": [{"name": "Державне управління управлінням справами"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertNotEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {
            "data": {
                "lotValues": [{"relatedLot": lot_id}],
                "tenderers": self.test_bids_data[0]["tenderers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["lotValues"][0]["date"], lot["date"])
    self.assertEqual(response.json["data"]["tenderers"][0]["name"], bidder["tenderers"][0]["name"])

    # If we don't change anything then return null
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"lotValues": [{"relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("lotValues", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bidder["id"], bid_token),
        {"data": {"lotValues": [{"relatedLot": lot_id}], "status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update bid in current (unsuccessful) tender status"
    )


# CompetitiveDialogueEULotFeatureBidderResourceTest

@patch("openprocurement.tender.core.models.TWO_PHASE_COMMIT_FROM", get_now() + timedelta(days=1))
def create_tender_with_features_bidder_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    bid_data["lotValues"] = [{"relatedLot": "0" * 32}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
                "location": "body",
                "name": "lotValues",
            }
        ],
    )

    # Field 'value' doesn't exists on first stage
    bid_data["lotValues"] = [{"relatedLot": self.lot_id}]

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


# CompetitiveDialogueEULotProcessTest
def one_lot_0bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    response = self.set_status("active.tendering")
    self.assertNotIn("auctionPeriod", response.json["data"]["lots"][0])
    # switch to unsuccessful
    self.set_status("active.stage2.pending", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["lots"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't add lot in current (unsuccessful) tender status"}],
    )


def one_lot_2bid_1unqualified(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder_data = bid_data["tenderers"][0]
    bidder_data["identifier"]["id"] = "00037256"
    self.create_bid(tender_id, bid_data, "pending")

    bidder_data["identifier"]["id"] = "00037257"
    self.create_bid(tender_id, bid_data, "pending")
    bidder_data["identifier"]["id"] = "00037258"
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[0]["id"], owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[1]["id"], owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[2]["id"], owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")


def one_lot_2bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder_data = bid_data["tenderers"][0]
    bidder_data["identifier"]["id"] = "00037256"
    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder_data["identifier"]["id"] = "00037257"
    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    # create third
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder_data["identifier"]["id"] = "00037258"
    bid, bid_token = self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.status, "200 OK")

    for bid in response.json["data"]["bids"]:
        self.assertEqual(bid["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")


def two_lot_2bid_1lot_del(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.test_tender_data["items"][0] for i in lots]}},
    )

    response = self.set_status("active.tendering")
    # create bid

    bids = []
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id} for lot_id in lots]
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bids.append(response.json)
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data["tenderers"] = self.test_bids_data[1]["tenderers"]
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    bids.append(response.json)
    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lots[0], owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def one_lot_3bid_1del(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bids
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder_data = bid_data["tenderers"][0]
    for index, test_bid in enumerate(self.test_bids_data):
        bidder_data["identifier"]["id"] = "00037256" + str(index)
        bid, token = self.create_bid(tender_id, bid_data, "pending")
        bids.append({bid["id"]: token})

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, list(bids[2].keys())[0], list(bids[2].values())[0])
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    # check tender status
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_3bid_1un(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    items[0]["relatedLot"] = lot_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": items}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id}]
    bidder_data = bid_data["tenderers"][0]
    for i in range(3):
        bidder_data["identifier"]["id"] = "00037256" + str(i)
        bid, token = self.create_bid(tender_id, bid_data, "pending")
        bids.append({bid["id"]: token})

    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        if qualification["bidID"] == list(bids[2].keys())[0]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "unsuccessful"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "unsuccessful")
        else:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()

    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]


def two_lot_0bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.test_tender_data["items"][0] for i in lots]}},
    )
    tender = response.json["data"]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")

    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    # switch to unsuccessful
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertTrue(all([i["status"] == "unsuccessful" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def two_lot_2can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.test_tender_data["items"][0] for i in lots]}},
    )
    tender = response.json["data"]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()
    # cancel every lot
    for lot_id in lots:
        cancellation = dict(**test_tender_below_cancellation)
        cancellation.update({
            "status": "active",
            "cancellationOf": "lot",
            "relatedLot": lot_id,
        })
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
            {"data": cancellation},
        )

        cancellation_id = response.json["data"]["id"]
        if RELEASE_2020_04_19 < get_now():
            activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def two_lot_2bid_0com_1can(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.test_tender_data["items"][0] for i in lots]}},
    )
    tender = response.json["data"]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id} for lot_id in lots]
    bidder_data = bid_data["tenderers"][0]
    bidder_data["identifier"]["id"] = "00037256"
    self.create_bid(tender_id, bid_data, "pending")

    bid_data["lotValues"] = [{"relatedLot": lot_id} for lot_id in lots]
    bidder_data["identifier"]["id"] = "00037257"
    self.create_bid(tender_id, bid_data, "pending")

    bidder_data["identifier"]["id"] = "00037258"
    self.create_bid(tender_id, bid_data, "pending")

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lots[0],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.status, "200 OK")
    # active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 3)

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")


def two_lot_2bid_2com_2win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.test_tender_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)
    lots = []
    for lot in 2 * self.test_lots_data:
        # add lot
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
        )
        self.assertEqual(response.status, "201 Created")
        lots.append(response.json["data"]["id"])
    self.initial_lots = lots
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [self.test_tender_data["items"][0] for i in lots]}},
    )
    tender = response.json["data"]
    # add relatedLot for item
    items = deepcopy(tender["items"])
    for n, i in enumerate(lots):
        items[n]["relatedLot"] = i
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"relatedLot": lot_id} for lot_id in lots]
    bidder_data = bid_data["tenderers"][0]
    bidder_data["identifier"]["id"] = "00037256"
    self.app.authorization = ("Basic", ("broker", ""))
    self.create_bid(tender_id, bid_data, "pending")
    # create second bid
    bidder_data["identifier"]["id"] = "00037257"
    self.create_bid(tender_id, bid_data, "pending")
    # create third bid
    bidder_data["identifier"]["id"] = "00037258"
    self.create_bid(tender_id, bid_data, "pending")
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 6)

    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
