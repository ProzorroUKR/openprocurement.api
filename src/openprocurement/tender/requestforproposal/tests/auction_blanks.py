from openprocurement.tender.belowthreshold.tests.auction_blanks import update_patch_data
from openprocurement.tender.core.tests.utils import activate_contract, change_auth
from openprocurement.tender.requestforproposal.tests.base import test_tender_rfp_claim


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

    if self.initial_data["procurementMethodType"] in ("requestForProposal",):
        self.set_status("active.enquiries")

    response = self.set_status("active.auction")

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

    patch_data = {"bids": [{"lotValues": [{}, {}, {}]} for b in self.initial_bids]}
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Number of lots of auction results did not match the number of tender lots"],
    )

    patch_data = {
        "bids": [
            {
                "lotValues": [
                    {"relatedLot": b["lotValues"][0]["relatedLot"]},
                    {"relatedLot": b["lotValues"][0]["relatedLot"]},
                ]
            }
            for b in self.initial_bids
        ]
    }
    response = self.app.post_json(f"/tenders/{self.tender_id}/auction/{lot_id}", {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"],
        ['Auction bid.lotValues should be identical to the tender bid.lotValues'],
    )

    num = 0
    for lot in self.initial_lots:
        patch_data["bids"] = [
            {"lotValues": [{"value": {"amount": 10**num}} for _ in b["lotValues"]]} for b in self.initial_bids
        ]

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


# TenderAuctionResourceDisabledAwardingOrder


def post_tender_auction_with_disabled_awarding_order(self):
    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")
    patch_data = {"bids": [{"value": {"amount": n}} for n, b in enumerate(self.initial_bids)]}
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    for n, b in enumerate(tender["bids"]):
        self.assertEqual(b["value"]["amount"], n)

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    self.assertEqual(len(tender["awards"]), 2)
    for award in tender["awards"]:
        self.assertEqual(award["status"], "pending")
    self.assertEqual(tender["awards"][0]["bid_id"], self.initial_bids[0]["id"])
    self.assertEqual(tender["awards"][0]["value"]["amount"], 0)
    self.assertEqual(tender["awards"][0]["suppliers"], self.initial_bids[0]["tenderers"])
    award_1_id = tender["awards"][0]["id"]
    award_2_id = tender["awards"][1]["id"]

    # The customer decides that the winner is award1
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(tender["awards"][0]["status"], "active")
    self.assertEqual(tender["awards"][1]["status"], "pending")
    self.assertEqual(tender["status"], "active.awarded")

    # Try to activate one more award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't activate award as tender already has active award",
                "location": "body",
                "name": "awards",
            }
        ],
    )

    # The customer cancels decision due to award1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 3)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")
    self.assertEqual(tender["awards"][1]["status"], "pending")
    self.assertEqual(tender["awards"][2]["status"], "pending")
    self.assertEqual(tender["status"], "active.qualification")
    award_3_id = tender["awards"][2]["id"]

    # The customer rejects award3 and recognizes as the winner award2
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_3_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 3)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")
    self.assertEqual(tender["awards"][1]["status"], "active")
    self.assertEqual(tender["awards"][2]["status"], "unsuccessful")
    self.assertEqual(tender["status"], "active.awarded")

    # cancel the winner and make all pending awards unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    award_4_id = tender["awards"][3]["id"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_4_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 4)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")
    self.assertEqual(tender["awards"][1]["status"], "cancelled")
    self.assertEqual(tender["awards"][2]["status"], "unsuccessful")
    self.assertEqual(tender["awards"][3]["status"], "unsuccessful")
    self.assertEqual(tender["status"], "active.awarded")


def post_tender_auction_with_disabled_awarding_order_cancelling_awards(self):
    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")
    patch_data = {"bids": [{"value": {"amount": n}} for n, b in enumerate(self.initial_bids)]}
    response = self.app.post_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    for n, b in enumerate(tender["bids"]):
        self.assertEqual(b["value"]["amount"], n)

    self.assertEqual("active.qualification", tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    self.assertEqual(len(tender["awards"]), 2)
    for award in tender["awards"]:
        self.assertEqual(award["status"], "pending")
    award_1_id = tender["awards"][0]["id"]
    award_2_id = tender["awards"][1]["id"]
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards/{award_1_id}/complaints",
            {"data": test_tender_rfp_claim},
        )
        self.assertEqual(response.status, "201 Created")

    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 3)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")
    self.assertEqual(tender["awards"][1]["status"], "unsuccessful")
    self.assertEqual(tender["awards"][2]["status"], "pending")
    self.assertEqual(tender["status"], "active.qualification")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update award in current (unsuccessful) status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def post_tender_lots_auction_with_disabled_awarding_order(self):
    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")
    auction_url = "http://auction.openprocurement.org"
    lot_id1 = self.initial_lots[0]["id"]
    lot_id2 = self.initial_lots[1]["id"]
    auction1_url = '{}/tenders/{}_{}'.format(auction_url, self.tender_id, lot_id1)
    auction2_url = '{}/tenders/{}_{}'.format(auction_url, self.tender_id, lot_id2)
    patch_data = {
        'lots': [
            {
                'id': lot_id1,
                'auctionUrl': auction1_url,
            },
            {
                'id': lot_id2,
                'auctionUrl': auction2_url,
            },
        ],
        'bids': [
            {
                "id": bid["id"],
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid["id"])},
                    {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid["id"])},
                ],
            }
            for bid in self.initial_bids
        ],
    }
    response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id1), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id2), {'data': patch_data})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json(
        '/tenders/{}/auction/{}'.format(self.tender_id, lot_id1),
        {
            'data': {
                'bids': [
                    {
                        "id": bid["id"],
                        "lotValues": [
                            {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in bid["lotValues"]
                        ],
                    }
                    for bid in auction_bids_data
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json(
        '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
        {
            'data': {
                'bids': [
                    {
                        "id": bid["id"],
                        "lotValues": [
                            {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in bid["lotValues"]
                        ],
                    }
                    for bid in auction_bids_data
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json["data"]

    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(len(tender["awards"]), 4)
    for award in tender["awards"]:
        self.assertEqual(award["status"], "pending")
    self.assertEqual(tender["status"], "active.qualification")
    award_1_id = tender["awards"][0]["id"]
    award_2_id = tender["awards"][1]["id"]
    award_3_id = tender["awards"][2]["id"]
    award_4_id = tender["awards"][3]["id"]

    # The customer decides that the winner is award1 for lot1
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(tender["awards"][0]["status"], "active")  # lot1
    self.assertEqual(tender["awards"][1]["status"], "pending")  # lot1
    self.assertEqual(tender["awards"][2]["status"], "pending")  # lot2
    self.assertEqual(tender["awards"][3]["status"], "pending")  # lot2
    # tender is still in qualification mode because there is no result for lot2 yet
    self.assertEqual(tender["status"], "active.qualification")

    # The customer decides that the winner is award3 for lot2
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_3_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(tender["awards"][0]["status"], "active")  # lot1
    self.assertEqual(tender["awards"][1]["status"], "pending")  # lot1
    self.assertEqual(tender["awards"][2]["status"], "active")  # lot2
    self.assertEqual(tender["awards"][3]["status"], "pending")  # lot2
    # tender is in awarded mode because there are results for lot1 and lot2
    self.assertEqual(tender["status"], "active.awarded")

    # Try to activate one more award for lot1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't activate award as tender already has active award for this lot",
                "location": "body",
                "name": "awards",
            }
        ],
    )

    # The customer cancels decision due to award1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 5)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")  # lot1
    self.assertEqual(tender["awards"][1]["status"], "pending")  # lot1
    self.assertEqual(tender["awards"][2]["status"], "active")  # lot2
    self.assertEqual(tender["awards"][3]["status"], "pending")  # lot2
    self.assertEqual(tender["awards"][4]["status"], "pending")  # lot1
    self.assertEqual(tender["status"], "active.qualification")
    award_5_id = tender["awards"][4]["id"]

    # The customer rejects award5 and recognizes as the winner award2
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_5_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 5)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")  # lot1
    self.assertEqual(tender["awards"][1]["status"], "active")  # lot1
    self.assertEqual(tender["awards"][2]["status"], "active")  # lot2
    self.assertEqual(tender["awards"][3]["status"], "pending")  # lot2
    self.assertEqual(tender["awards"][4]["status"], "unsuccessful")  # lot1
    self.assertEqual(tender["status"], "active.awarded")

    # cancel the winner and make all pending awards unsuccessful
    # lot 1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    award_6_id = tender["awards"][5]["id"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_6_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    # lot 2
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_3_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    award_7_id = tender["awards"][6]["id"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_7_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_4_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(len(tender["awards"]), 7)
    self.assertEqual(tender["awards"][0]["status"], "cancelled")  # lot1
    self.assertEqual(tender["awards"][1]["status"], "cancelled")  # lot1
    self.assertEqual(tender["awards"][2]["status"], "cancelled")  # lot2
    self.assertEqual(tender["awards"][3]["status"], "unsuccessful")  # lot2
    self.assertEqual(tender["awards"][4]["status"], "unsuccessful")  # lot1
    self.assertEqual(tender["awards"][5]["status"], "unsuccessful")  # lot1
    self.assertEqual(tender["awards"][6]["status"], "unsuccessful")  # lot2
    self.assertEqual(tender["status"], "active.awarded")


def post_tender_lots_auction_with_disabled_awarding_order_lot_not_become_unsuccessful_with_active_award(self):
    self.app.authorization = ("Basic", ("auction", ""))
    self.set_status("active.auction")
    auction_url = "http://auction.openprocurement.org"
    lot_id1 = self.initial_lots[0]["id"]
    lot_id2 = self.initial_lots[1]["id"]
    auction1_url = '{}/tenders/{}_{}'.format(auction_url, self.tender_id, lot_id1)
    auction2_url = '{}/tenders/{}_{}'.format(auction_url, self.tender_id, lot_id2)
    patch_data = {
        'lots': [
            {
                'id': lot_id1,
                'auctionUrl': auction1_url,
            },
            {
                'id': lot_id2,
                'auctionUrl': auction2_url,
            },
        ],
        'bids': [
            {
                "id": bid["id"],
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid["id"])},
                    {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid["id"])},
                ],
            }
            for bid in self.initial_bids
        ],
    }
    response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id1), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id2), {'data': patch_data})
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json(
        '/tenders/{}/auction/{}'.format(self.tender_id, lot_id1),
        {
            'data': {
                'bids': [
                    {
                        "id": bid["id"],
                        "lotValues": [
                            {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in bid["lotValues"]
                        ],
                    }
                    for bid in auction_bids_data
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    response = self.app.post_json(
        '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
        {
            'data': {
                'bids': [
                    {
                        "id": bid["id"],
                        "lotValues": [
                            {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in bid["lotValues"]
                        ],
                    }
                    for bid in auction_bids_data
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    tender = response.json["data"]

    self.assertEqual("active.qualification", tender["status"])
    self.assertEqual(len(tender["awards"]), 4)
    for award in tender["awards"]:
        self.assertEqual(award["status"], "pending")
    self.assertEqual(tender["status"], "active.qualification")
    award_1_id = tender["awards"][0]["id"]
    award_2_id = tender["awards"][1]["id"]
    award_3_id = tender["awards"][2]["id"]
    award_4_id = tender["awards"][3]["id"]

    # The customer decides that the winner is award1 for lot1
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_1_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    # The customer reject award2 for lot1
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_2_id, self.tender_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    self.assertEqual(response.status, "200 OK")
    # The customer decides that the winner is award3 for lot2
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, award_3_id, self.tender_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    tender = response.json["data"]
    self.assertEqual(tender["awards"][0]["status"], "active")  # lot1
    self.assertEqual(tender["awards"][1]["status"], "unsuccessful")  # lot1
    self.assertEqual(tender["awards"][2]["status"], "active")  # lot2
    self.assertEqual(tender["awards"][3]["status"], "pending")  # lot2
    self.assertEqual(tender["lots"][0]["status"], "active")
    self.assertEqual(tender["lots"][1]["status"], "active")

    contracts_response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)

    # prepare contract for activating
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    # in case any contract become active and there are no pending contracts -> tender should have complete status
    activate_contract(
        self, self.tender_id, contracts[0]["id"], self.tender_token, list(self.initial_bids_tokens.values())[0]
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["status"], "complete")  # because second contract still in pending

    activate_contract(
        self, self.tender_id, contracts[1]["id"], self.tender_token, list(self.initial_bids_tokens.values())[0]
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")

    lots = response.json["data"]["lots"]
    for lot in lots:
        self.assertEqual(lot["status"], "complete")
