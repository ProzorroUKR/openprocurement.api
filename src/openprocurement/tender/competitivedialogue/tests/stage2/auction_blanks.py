# -*- coding: utf-8 -*-


# TenderStage2EU(UA)MultipleLotAuctionResourceTest
from openprocurement.tender.belowthreshold.tests.base import test_cancellation
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19


def patch_tender_with_lots_auction(self):
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update auction urls in current ({}) tender status".format(self.forbidden_auction_actions_status),
    )

    self.set_status("active.auction")
    response = self.check_chronograph()

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
                "id": self.bids[1]["id"],
                "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                    self.tender_id, self.bids[1]["id"]
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
                self.tender_id, self.bids[0]["id"]
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
    auctionUrl = patch_data.pop("auctionUrl")
    patch_data["lots"] = [{"auctionUrl": auctionUrl}, {"auctionUrl": auctionUrl}]
    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    patch_data["bids"].append(
        {
            "lotValues": [
                {
                    "participationUrl": u"http://auction-sandbox.openprocurement.org/tenders/{}?key_for_bid={}".format(
                        self.tender_id, self.bids[0]["id"]
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

    patch_data["bids"][1]["id"] = self.bids[0]["id"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{u"lotValues": [u"Number of lots of auction results did not match the number of tender lots"]}],
    )

    patch_data["lots"] = [patch_data["lots"][0].copy() for i in self.lots]
    patch_data["lots"][1]["id"] = "00000000000000000000000000000000"

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [
            {u"lots": [{u"id": [u"id should be one of lots"]}]},
            {u"lots": [{u"id": [u"id should be one of lots"]}]},
            {u"lots": [{u"id": [u"id should be one of lots"]}]},
        ],
    )

    patch_data["lots"][1]["id"] = self.lots[1]["id"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}],
    )

    for bid in patch_data["bids"]:
        bid["lotValues"] = [bid["lotValues"][0].copy() for i in self.lots]

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.bids[0]["lotValues"][0]["relatedLot"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json['errors'][0]["description"],
    # [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(
        response.json["errors"][0]["description"], [{u"lotValues": [u"bids don't allow duplicated proposals"]}]
    )

    patch_data["bids"][0]["lotValues"][1]["relatedLot"] = self.bids[0]["lotValues"][1]["relatedLot"]

    response = self.app.patch_json("/tenders/{}/auction".format(self.tender_id), {"data": patch_data})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIsNone(response.json)

    for lot in self.lots:
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

    self.app.authorization = ("Basic", ("broker", ""))
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.lots[0]["id"],
    })

    if RELEASE_2020_04_19 > get_now():

        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")

        cancelled_lot_id = self.lots[0]["id"]

        for bid in patch_data["bids"]:
            ## delete lotValues for cancelled lot in patch data
            bid["lotValues"] = [bid["lotValues"][1]]

        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.patch_json(
            "/tenders/{}/auction/{}".format(self.tender_id, self.lots[0]["id"]), {"data": patch_data}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can update auction urls only in active lot status")
