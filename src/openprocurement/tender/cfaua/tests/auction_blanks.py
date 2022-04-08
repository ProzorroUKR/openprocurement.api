# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.auction_blanks import update_patch_data


def post_tender_1lot_auction_not_changed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")

    data = [
        {
            "lotValues": [{"value": b["lotValues"][0]["value"]}]
        } for b in self.initial_bids
    ]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, response.json["data"]["lots"][0]["id"]),
        {"data": {"bids": data}},
    )
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[0]["id"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"])


def post_tender_1lot_auction_reversed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    now = get_now()
    patch_data = {"bids": []}
    for i, b in enumerate(self.initial_bids):
        lot_values = [{"value": deepcopy(b["lotValues"][0]["value"]), "date": (now - timedelta(seconds=i)).isoformat()}]
        patch_data["bids"].append({"id": b["id"], "lotValues": lot_values})

    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]), {"data": patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[-1]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], self.initial_bids[-1]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[-1]["tenderers"])


def post_tender_auction_all_awards_pending(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")

    patch_data = {"bids": []}
    for x, b in enumerate(self.initial_bids):
        lot_values = [{"value": deepcopy(b["lotValues"][0]["value"])}]
        lot_values[0]["value"]["amount"] = 409 + x * 10
        patch_data["bids"].append({"id": b["id"], "lotValues": lot_values})

    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]), {"data": patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    for x in range(self.min_bids_number):
        self.assertEqual(
            tender["bids"][x]["lotValues"][0]["value"]["amount"],
            patch_data["bids"][x]["lotValues"][0]["value"]["amount"],
        )
        self.assertEqual(tender["awards"][x]["status"], "pending")  # all awards are in pending status

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("broker", ""))
    awards = response.json["data"]

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
        "Can't switch to 'active.qualification.stand-still' while not all awards are qualified",
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


def tender_go_to_awarded_with_one_lot(self):
    response = self.set_status("active.auction")
    self.assertEqual(response.status, "200 OK")
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    auction_bids_data = response.json["data"]["bids"]
    auction_lot_data = response.json["data"]["lots"]
    if auction_lot_data:
        for lot in auction_lot_data:
            auction_bids_data = [
                {"lotValues": [{"value": b["lotValues"][0]["value"]}]}
                for b in auction_bids_data
            ]
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": {"bids": auction_bids_data}}
            )
    else:  # this procedure has always one lot, wtf is this branch ?
        response = self.app.post_json(
            "/tenders/{}/auction".format(self.tender_id), {"data": {"bids": auction_bids_data}}
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    awards = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, awards[0]["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # try to switch not all awards qualified
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't switch to 'active.qualification.stand-still' while not all awards are qualified",
    )
    # qualified all awards
    for award in awards[1:]:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
    # switch to active.qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.qualification.stand-still"}},
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")

    # switch to active.awarded
    self.set_status("active.qualification.stand-still", "end")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")


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
        response.json["errors"][0]["description"], "Number of auction results did not match the number of tender bids"
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
    self.assertEqual(response.json["errors"][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data["bids"][-1]["id"] = self.initial_bids[0]["id"]

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    max_awards = tender["maxAwardsCount"]
    self.assertNotEqual(tender["bids"][0]["value"]["amount"], self.initial_bids[0]["value"]["amount"])
    self.assertNotEqual(tender["bids"][-1]["value"]["amount"], self.initial_bids[-1]["value"]["amount"])
    self.assertEqual(tender["bids"][0]["value"]["amount"], patch_data["bids"][-1]["value"]["amount"])
    self.assertEqual(tender["bids"][-1]["value"]["amount"], patch_data["bids"][0]["value"]["amount"])
    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    if len(self.initial_bids) > max_awards:
        self.assertEqual(len(tender["awards"]), max_awards)
    else:
        self.assertLessEqual(len(tender["awards"]), max_awards)

    for x in list(range(self.min_bids_number))[:max_awards]:
        self.assertEqual(tender["awards"][x]["bid_id"], patch_data["bids"][x]["id"])
        self.assertEqual(tender["awards"][x]["value"]["amount"], patch_data["bids"][x]["value"]["amount"])
        self.assertEqual(tender["awards"][x]["suppliers"], self.initial_bids[x]["tenderers"])

    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )


# TenderLotAuctionResourceTestMixin


def post_tender_lot_auction(self):
    lot_id = self.initial_lots[0]["id"]
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    response = self.app.post_json(
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

    patch_data["bids"][0]["id"] = self.initial_bids[0]["id"]
    patch_data["bids"][-1]["id"] = self.initial_bids[-1]["id"]

    for lot in self.initial_lots:
        response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot["id"]), {"data": patch_data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]

    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"],
        patch_data["bids"][0]["lotValues"][0]["value"]["amount"],
    )
    self.assertEqual(
        tender["bids"][1]["lotValues"][0]["value"]["amount"],
        patch_data["bids"][1]["lotValues"][0]["value"]["amount"],
    )

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    max_awards = tender.get("maxAwardsCount", 1000)
    if len(self.initial_bids) > max_awards:
        self.assertEqual(len(tender["awards"]), max_awards)
    else:
        self.assertLessEqual(len(tender["awards"]), max_awards)

    tender_bids = [
        b for b in sorted(self.mongodb.tenders.get(self.tender_id)["bids"],
                          key=lambda b: (float(b["lotValues"][0]["value"]["amount"]), b["date"]))
    ]
    for x in list(range(self.min_bids_number))[:max_awards]:
        self.assertEqual(tender["awards"][x]["bid_id"], tender_bids[x]["id"])
        self.assertEqual(
            tender["awards"][x]["value"]["amount"], float(tender_bids[x]["lotValues"][0]["value"]["amount"])
        )
        self.assertEqual(tender["awards"][x]["suppliers"], tender_bids[x]["tenderers"])

    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )
