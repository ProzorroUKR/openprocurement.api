from openprocurement.tender.belowthreshold.tests.auction_blanks import update_patch_data


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
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(
        auction["bids"][0]["lotValues"][0]["value"]["amount"],
        self.initial_bids[0]["lotValues"][0]["value"]["amount"],
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][0]["value"]["amount"],
        self.initial_bids[1]["lotValues"][0]["value"]["amount"],
    )
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
                "lotValues": [{"value": {"amount": 409, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": patch_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], ["Number of auction results did not match the number of tender bids"]
    )

    update_patch_data(self, patch_data, key="lotValues", start=-2, interval=-1)

    patch_data["bids"] = [{"lotValues": [{"value": {"amount": n}}]} for n, b in enumerate(self.initial_bids)]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, self.initial_lots[0]["id"]),
        {"data": patch_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    for n, b in enumerate(tender["bids"]):
        self.assertEqual(b["lotValues"][0]["value"]["amount"], n)

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


def post_tender_auction_not_changed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    lot_id = self.initial_lots[0]["id"]
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
        {"data": {"bids": [{"lotValues": [{"value": bid["value"]}]} for bid in self.test_bids_data]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], self.initial_bids[0]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])


def post_tender_auction_reversed(self):
    self.app.authorization = ("Basic", ("auction", ""))
    lot_id = self.initial_lots[0]["id"]
    patch_data = {"bids": [{"lotValues": [{"value": bid["value"]}]} for bid in self.test_bids_data]}

    response = self.app.post_json("/tenders/{}/auction/{}".format(self.tender_id, lot_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], self.initial_bids[-1]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[-1]["tenderers"])


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
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(
        auction["bids"][0]["lotValues"][0]["value"]["amount"],
        self.initial_bids[0]["lotValues"][0]["value"]["amount"],
    )
    self.assertEqual(
        auction["bids"][1]["lotValues"][0]["value"]["amount"],
        self.initial_bids[1]["lotValues"][0]["value"]["amount"],
    )
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

    lot_id = self.initial_lots[0]["id"]
    patch_data = {
        "bids": [
            {
                "lotValues": [{"value": {"amount": 459, "currency": "UAH", "valueAddedTaxIncluded": True}}],
            }
        ]
    }

    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
        {"data": patch_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], ["Number of auction results did not match the number of tender bids"]
    )

    update_patch_data(self, patch_data, key="value", start=-2, interval=-1)

    patch_data = {
        "bids": [
            {"lotValues": [{"value": {"amount": 11111}}]},
            {"lotValues": [{"value": {"amount": 2222}}]},
        ]
    }
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
        {"data": patch_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("features", tender)
    self.assertIn("parameters", tender["bids"][0])
    self.assertEqual(
        tender["bids"][0]["lotValues"][0]["value"]["amount"], patch_data["bids"][0]["lotValues"][0]["value"]["amount"]
    )
    self.assertEqual(
        tender["bids"][1]["lotValues"][0]["value"]["amount"],
        patch_data["bids"][1]["lotValues"][0]["value"]["amount"],
    )

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    # bids have same amount, but bid with better parameters awarded
    self.assertEqual(tender["awards"][0]["bid_id"], tender["bids"][1]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], tender["bids"][1]["lotValues"][0]["value"]["amount"])
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[1]["tenderers"])

    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
        {"data": patch_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't report auction results in current (active.qualification) tender status",
    )
