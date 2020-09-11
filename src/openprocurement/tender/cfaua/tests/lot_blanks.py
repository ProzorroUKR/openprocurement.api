# -*- coding: utf-8 -*-
import mock
from copy import deepcopy
from datetime import timedelta
from email.header import Header

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_cancellation, test_claim


def get_tender_lot(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    lot = response.json["data"]["lots"][0]

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        set(response.json["data"]),
        set([u"status", u"date", u"description", u"title", u"minimalStep", u"auctionPeriod", u"value", u"id"]),
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    api_lot = response.json["data"]
    lot.pop("auctionPeriod")
    api_lot.pop("auctionPeriod")
    self.assertEqual(api_lot, lot)

    response = self.app.get("/tenders/{}/lots/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"lot_id"}])

    response = self.app.get("/tenders/some_id/lots/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_lots(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    lot = response.json["data"]["lots"][0]

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        set(response.json["data"][0]),
        set([u"status", u"description", u"date", u"title", u"minimalStep", u"auctionPeriod", u"value", u"id"]),
    )

    self.set_status("active.qualification")

    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    api_lot = response.json["data"][0]
    lot.pop("auctionPeriod")
    api_lot.pop("auctionPeriod")
    self.assertEqual(api_lot, lot)

    response = self.app.get("/tenders/some_id/lots", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def patch_tender_currency(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    lot = response.json["data"]["lots"][0]
    self.assertEqual(lot["value"]["currency"], "UAH")

    # update tender currency without mimimalStep currency change
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"currency": "GBP"}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"currency should be identical to currency of value of tender"],
                u"location": u"body",
                u"name": u"minimalStep",
            }
        ],
    )

    # update tender currency
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"currency": "GBP"}, "minimalStep": {"currency": "GBP"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # log currency is updated too
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")

    # try to update lot currency
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")

    # try to update minimalStep currency
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"minimalStep": {"currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["minimalStep"]["currency"], "GBP")

    # try to update lot minimalStep currency and lot value currency in single request
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertEqual(lot["value"]["currency"], "GBP")
    self.assertEqual(lot["minimalStep"]["currency"], "GBP")


def patch_tender_lot(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    lot = response.json["data"]["lots"][0]

    with mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.patch_json(
            "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
            {"data": {"minimalStep": {"amount": 35.0}}}, status=422
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{u"description": [u"minimalstep must be between 0.5% and 3% of value (with 2 digits precision)."],
              u"location": u"body", u"name": u"minimalStep"}]
        )

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"title": "new title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "new title")

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"guarantee": {"amount": 12}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"guarantee": {"currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    # Deleted self.assertEqual(response.body, 'null') to make this test OK in other procedures,
    # because there is a bug with invalidation bids at openua, openeu and openuadefence that makes body not null

    response = self.app.patch_json(
        "/tenders/{}/lots/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"title": "other title"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"lot_id"}])

    response = self.app.patch_json("/tenders/some_id/lots/some_id", {"data": {"title": "other title"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["title"], "new title")

    self.set_status("{}".format(self.forbidden_lot_actions_status))

    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"title": "other title"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update lot in current ({}) tender status".format(self.forbidden_lot_actions_status),
    )


def patch_tender_vat(self):
    # set tender VAT
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")

    # get lot
    response = self.app.get("/tenders/{}/lots".format(self.tender_id))
    lot = response.json["data"][0]
    self.assertTrue(lot["value"]["valueAddedTaxIncluded"])

    # update tender VAT
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False}, "minimalStep": {"valueAddedTaxIncluded": False}}},
    )
    self.assertEqual(response.status, "200 OK")
    # log VAT is updated too
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["value"]["valueAddedTaxIncluded"])

    # try to update lot VAT
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["value"]["valueAddedTaxIncluded"])

    # try to update minimalStep VAT
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["minimalStep"]["valueAddedTaxIncluded"])

    # try to update minimalStep VAT and value VAT in single request
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, lot["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True}, "minimalStep": {"valueAddedTaxIncluded": True}}},
    )
    self.assertEqual(response.status, "200 OK")
    # but the value stays unchanged
    response = self.app.get("/tenders/{}/lots/{}".format(self.tender_id, lot["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    lot = response.json["data"]
    self.assertFalse(lot["value"]["valueAddedTaxIncluded"])
    self.assertEqual(lot["minimalStep"]["valueAddedTaxIncluded"], lot["value"]["valueAddedTaxIncluded"])


def two_lot_3bid_3com_3win(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
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
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [{"relatedLot": i} for i in lots]}},
    )
    self.assertEqual(response.status, "200 OK")
    # create bids
    for x in range(self.min_bids_number):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {
                "data": {
                    "selfEligible": True,
                    "selfQualified": True,
                    "tenderers": self.test_bids_data[0]["tenderers"],
                    "lotValues": [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id} for lot_id in lots],
                }
            },
        )

    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number * 2)

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
    # switch to active.auction
    self.time_shift("active.auction")
    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in lots:
        # posting auction urls
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
        # posting auction results
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(tender_id, lot_id), {"data": {"bids": auction_bids_data}}
        )
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # for second lot
    lot_id = lots[1]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertTrue(all([i["status"] == "complete" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_2bid(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": [{"relatedLot": lot_id}]}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bids
    for x in range(self.min_bids_number):
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {
                "data": {
                    "selfEligible": True,
                    "selfQualified": True,
                    "tenderers": self.test_bids_data[x]["tenderers"],
                    "lotValues": [{"value": self.test_bids_data[x]["value"], "relatedLot": lot_id}],
                }
            },
        )
        if x == 0:
            bid_id = response.json["data"]["id"]
            bid_token = response.json["access"]["token"]

    # switch to active.auction
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

    self.time_shift("active.auction")

    self.check_chronograph()

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    response = self.app.patch_json(
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
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id), {"data": {"bids": auction_bids_data}}
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # after stand slill period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_3bid_1del(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": [{"relatedLot": lot_id}]}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bids
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    for i in range(self.min_bids_number + 1):
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {
                "data": {
                    "selfEligible": True,
                    "selfQualified": True,
                    "tenderers": self.test_bids_data[0]["tenderers"],
                    "lotValues": [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}],
                }
            },
        )
        bids.append({response.json["data"]["id"]: response.json["access"]["token"]})

    response = self.app.delete(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bids[2].keys()[0], bids[2].values()[0])
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
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

    self.time_shift("active.auction")

    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": list(auction_bids_data),
        }
    }

    for bid_index, bid in enumerate(auction_bids_data):
        if bid.get("status", "active") == "active":
            for lot_index, lot_bid in enumerate(bid["lotValues"]):
                if lot_bid["relatedLot"] == lot_id and lot_bid.get("status", "active") == "active":
                    data["data"]["bids"][bid_index]["lotValues"][lot_index][
                        "participationUrl"
                    ] = "https://tender.auction.url/for_bid/{}".format(bid["id"])
                    break

    response = self.app.patch_json("/tenders/{}/auction/{}".format(tender_id, lot_id), data)
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    bid_id = bids[0].keys()[0]
    bid_token = bids[0].values()[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    bid_id = bids[2].keys()[0]
    bid_token = bids[2].values()[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json["data"]["status"], "deleted")

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id), {"data": {"bids": auction_bids_data}}
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # after stand slill period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def one_lot_3bid_1un(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # add lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    lot_id = response.json["data"]["id"]
    self.initial_lots = [response.json["data"]]
    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"items": [{"relatedLot": lot_id}]}}
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bids = []
    for i in range(self.min_bids_number + 1):
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {
                "data": {
                    "selfEligible": True,
                    "selfQualified": True,
                    "tenderers": self.test_bids_data[0]["tenderers"],
                    "lotValues": [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}],
                }
            },
        )
        bids.append({response.json["data"]["id"]: response.json["access"]["token"]})

    # switch to active.auction
    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    for qualification in qualifications:
        if qualification["bidID"] == bids[2].keys()[0]:
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

    self.time_shift("active.auction")

    self.check_chronograph()
    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    data = {
        "data": {
            "lots": [
                {"id": i["id"], "auctionUrl": "https://tender.auction.url"} for i in response.json["data"]["lots"]
            ],
            "bids": list(auction_bids_data),
        }
    }

    for bid_index, bid in enumerate(auction_bids_data):
        if bid.get("status", "active") == "active":
            for lot_index, lot_bid in enumerate(bid["lotValues"]):
                if lot_bid["relatedLot"] == lot_id and lot_bid.get("status", "active") == "active":
                    data["data"]["bids"][bid_index]["lotValues"][lot_index][
                        "participationUrl"
                    ] = "https://tender.auction.url/for_bid/{}".format(bid["id"])
                    break

    response = self.app.patch_json("/tenders/{}/auction/{}".format(tender_id, lot_id), data)
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    bid_id = bids[0].keys()[0]
    bid_token = bids[0].values()[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    bid_id = bids[2].keys()[0]
    bid_token = bids[2].values()[0]
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertNotIn("lotValues", response.json["data"])

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction/{}".format(tender_id, lot_id), {"data": {"bids": auction_bids_data}}
    )
    # # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # after stand slill period

    self.time_shift("complete")
    self.check_chronograph()

    # # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["lots"][0]["status"], "complete")
    self.assertEqual(response.json["data"]["status"], "complete")


def two_lot_3bid_1win_bug(self):
    """
    ref: http://prozorro.worksection.ua/project/141436/3931481/#com9856686
    """
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data})
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
        {"data": {"items": [self.initial_data["items"][0] for i in lots]}},
    )
    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"items": [{"relatedLot": i} for i in lots]}},
    )
    self.assertEqual(response.status, "200 OK")
    # create bids
    self.app.authorization = ("Basic", ("broker", ""))
    for x in range(self.min_bids_number):
        response = self.app.post_json(
            "/tenders/{}/bids".format(tender_id),
            {
                "data": {
                    "selfEligible": True,
                    "selfQualified": True,
                    "tenderers": self.test_bids_data[x]["tenderers"],
                    "lotValues": [{"value": self.test_bids_data[x]["value"], "relatedLot": lot_id} for lot_id in lots],
                }
            },
        )

    # create last bid
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "selfEligible": True,
                "selfQualified": True,
                "tenderers": self.test_bids_data[self.min_bids_number - 1]["tenderers"],
                "lotValues": [
                    {"value": self.test_bids_data[self.min_bids_number - 1]["value"], "relatedLot": lot_id}
                    for lot_id in lots
                ],
            }
        },
    )
    bid_id = response.json["data"]["id"]
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, owner_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), (self.min_bids_number + 1) * 2)

    for qualification in qualifications:
        if lots[1] == qualification["lotID"] and bid_id == qualification["bidID"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "unsuccessful"}},
            )
        else:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], owner_token),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
        self.assertEqual(response.status, "200 OK")
        if lots[1] == qualification["lotID"] and bid_id == qualification["bidID"]:
            self.assertEqual(response.json["data"]["status"], "unsuccessful")
        else:
            self.assertEqual(response.json["data"]["status"], "active")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.auction
    self.time_shift("active.auction")
    self.check_chronograph()

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    for lot_id in lots:
        # posting auction urls
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
        # posting auction results
        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.post_json(
            "/tenders/{}/auction/{}".format(tender_id, lot_id), {"data": {"bids": auction_bids_data}}
        )
    # for first lot
    lot_id = lots[0]
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get agreement id
    response = self.app.get("/tenders/{}".format(tender_id))
    agreement_id = response.json["data"]["agreements"][-1]["id"]
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # sign agreement
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(tender_id, agreement_id, owner_token),
        {"data": {"status": "active"}},
    )
    # for second lot
    lot_id = lots[1]

    for x in range(self.min_bids_number):
        # get awards
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
        # get pending award
        award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id][0]
        # set award as unsuccessful
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
            {"data": {"status": "unsuccessful"}},
        )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    self.assertEqual([i["id"] for i in response.json["data"] if i["status"] == "pending" and i["lotID"] == lot_id], [])
    # after stand slill period
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.db.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)
    # ping by chronograph
    self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(set([i["status"] for i in response.json["data"]["lots"]]), set(["complete", "unsuccessful"]))
    self.assertEqual(response.json["data"]["status"], "complete")


def proc_1lot_1can(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))

    lot_id = response.json["data"]["lots"][0]["id"]
    # add item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": [{"relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to active.tendering
    # TODO: set auctionPeriod.startDate for lots
    # response = self.set_status('active.tendering', {"lots": [
    #     {"auctionPeriod": {"startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()}}
    # ]})
    # self.assertTrue(all(["auctionPeriod" in i for i in response.json['data']['lots']]))
    # cancel lot

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": lot_id,
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertTrue(all([i["status"] == "cancelled" for i in response.json["data"]["lots"]]))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def create_tender_lot(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["lots"] = deepcopy(self.initial_lots)
    tender_data["lots"][0]["minimalStep"]["amount"] = 35

    with mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": tender_data}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{u'description': [
                {u'minimalStep': [u'minimalstep must be between 0.5% and 3% of value (with 2 digits precision).']}],
              u'location': u'body', u'name': u'lots'}],
        )

    tender_data = deepcopy(self.initial_data)
    tender_data["lots"] = deepcopy(self.initial_lots)
    tender_data["lots"][0]["guarantee"] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": tender_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    data = response.json["data"]
    self.assertIn("guarantee", data["lots"][0])
    self.assertEqual(data["lots"][0]["guarantee"]["amount"], 100500)
    self.assertEqual(data["lots"][0]["guarantee"]["currency"], "USD")
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")
    self.assertIn("guarantee", response.json["data"]["lots"][0])

    # Create second lot with error
    lot2 = deepcopy(self.test_lots_data[0])
    lot2["guarantee"] = {"amount": 500, "currency": "UAH"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot2}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Please provide no more than 1 item."], u"location": u"body", u"name": u"lots"}],
    )

    lot2["guarantee"] = {"currency": "USD"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot2}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"amount": [u"This field is required."]}, u"location": u"body", u"name": u"guarantee"}],
    )

    lot2["guarantee"] = {"amount": 100600}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token), {"data": lot2}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Please provide no more than 1 item."], u"location": u"body", u"name": u"lots"}],
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"guarantee": {"currency": "EUR"}}},
    )
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "EUR")
    self.assertIn("guarantee", response.json["data"]["lots"][0])
    self.assertEqual(len(response.json["data"]["lots"]), 1)

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": self.test_lots_data[0]},
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Please provide no more than 1 item."], u"location": u"body", u"name": u"lots"}],
    )


def tender_lot_guarantee(self):
    data = deepcopy(self.initial_data)
    data["lots"] = deepcopy(self.initial_lots)
    data["lots"][0]["guarantee"] = {"amount": 20, "currency": "USD"}
    data["guarantee"] = {"amount": 100, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": data})
    tender = response.json["data"]
    tender_token = response.json["access"]["token"]
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    lot = deepcopy(self.test_lots_data[0])
    lot_id = response.json["data"]["lots"][0]["id"]

    self.assertIn("guarantee", response.json["data"]["lots"][0])
    self.assertEqual(response.json["data"]["lots"][0]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["lots"][0]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], tender_token), {"data": {"guarantee": {"currency": "GBP"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    lot["guarantee"] = {"amount": 20, "currency": "GBP"}
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender["id"], tender_token), {"data": lot}, status=422
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Please provide no more than 1 item."], u"location": u"body", u"name": u"lots"}],
    )

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], tender_token), {"data": {"guarantee": {"amount": 55}}}
    )
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 20)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")
    response = self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(tender["id"], lot_id, tender_token),
        {"data": {"guarantee": {"amount": 0, "currency": "GBP"}}},
    )
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 0)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 0)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")

    response = self.app.delete(
        "/tenders/{}/lots/{}?acc_token={}".format(tender["id"], lot_id, tender_token), status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "lots", "description": ["Please provide at least 1 item."]}],
    )

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 0)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "GBP")


# TenderLotEdgeCasesTest


def question_blocking(self):

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/questions".format(self.tender_id),
        {
            "data": {
                "title": "question title",
                "description": "question description",
                "questionOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
                "author": self.test_author,
            }
        },
    )
    question = response.json["data"]
    self.assertEqual(question["questionOf"], "lot")
    self.assertEqual(question["relatedItem"], self.initial_lots[0]["id"])

    self.set_status("active.tendering", "end")
    response = self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # cancel lot
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def claim_blocking(self):
    self.app.authorization = ("Basic", ("broker", ""))
    claim_data = deepcopy(test_claim)
    claim_data["relatedLot"] = self.initial_lots[0]["id"]
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": claim_data
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    self.assertEqual(complaint["relatedLot"], self.initial_lots[0]["id"])

    self.set_status("active.tendering", "end")
    response = self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    # cancel lot
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


# Tender Lot Feature Resource Test


def tender_value(self):
    request_path = "/tenders/{}".format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["value"]["amount"], sum([i["value"]["amount"] for i in self.initial_lots]))
    self.assertEqual(
        response.json["data"]["minimalStep"]["amount"], min([i["minimalStep"]["amount"] for i in self.initial_lots])
    )


def tender_features_invalid(self):
    request_path = "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token)
    data = self.initial_data.copy()
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = [
        {
            "featureOf": "lot",
            "relatedItem": self.initial_lots[0]["id"],
            "title": u"Потужність всмоктування",
            "enum": [{"value": 0.1, "title": u"До 1000 Вт"}, {"value": 0.15, "title": u"Більше 1000 Вт"}],
        }
    ]

    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Features are not allowed for lots"], u"location": u"body", u"name": u"features"}],
    )

    data["features"] = [
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": u"Відстрочка платежу",
            "description": u"Термін відстрочки платежу",
            "enum": [
                {"value": self.invalid_feature_value, "title": u"До 90 днів"},
                {"value": 0.1, "title": u"Більше 90 днів"},
            ],
        }
    ]
    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [
                    {u"enum": [{u"value": [u"Value should be less than {}.".format(self.max_feature_value)]}]}
                ],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )

    data["features"][0]["enum"][0]["value"] = 0.3
    data["features"].append(data["features"][0].copy())
    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Feature code should be uniq for all features"],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )

    data["features"][1]["code"] = "OCDS-123456-POSTPONEMENT"  # should be different
    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Sum of max value of all features for lot should be less then or equal to 30%"],
                u"location": u"body",
                u"name": u"features",
            }
        ],
    )

    tender = self.db.get(self.tender_id)
    tender["lots"] = []
    del tender["items"][0]["relatedLot"]
    self.db.save(tender)
    response = self.app.patch_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Please provide at least 1 item."], u"location": u"body", u"name": u"lots"}],
    )


def one_lot_1bid(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))

    lot_id = response.json["data"]["lots"][0]["id"]

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"value": self.test_bids_data[0]["value"], "relatedLot": lot_id}]
    del bid_data["value"]

    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": [{"relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(self.tender_id),
        {"data": bid_data},
    )
    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.check_chronograph()
    # switch to unsuccessful
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def tender_lot_document(self):
    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", str(Header(u"укр.doc", "utf-8")), "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    # dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "lot"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "lot", "relatedItem": "0" * 32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"relatedItem should be one of lots"], u"location": u"body", u"name": u"relatedItem"}],
    )

    # get tender for lot id
    response = self.app.get("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), status=200)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    # add document with lot_id
    lot_id = tender["lots"][0]["id"]
    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "lot", "relatedItem": lot_id}},
        status=200,
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["relatedItem"], lot_id)


def proc_1lot_0bid(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))

    lot_id = response.json["data"]["lots"][0]["id"]
    # add relatedLot for item

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": [{"relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    # switch to unsuccessful
    response = self.set_status("active.tendering", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json["data"]["lots"][0]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def one_lot_2bid_1unqualified(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    lot_id = response.json["data"]["lots"][0]["id"]

    # add relatedLot for item
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"items": [{"relatedLot": lot_id}]}},
    )
    self.assertEqual(response.status, "200 OK")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]

    for i in range(self.min_bids_number):
        bid_data["lotValues"] = [{"value": self.test_bids_data[i]["value"], "relatedLot": lot_id}]
        bid_data["tenderers"] = self.test_bids_data[i]["tenderers"]
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )

    # switch to active.pre-qualification
    self.set_status("active.tendering", "end")
    self.check_chronograph()

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.app.authorization = ("Basic", ("token", ""))
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(
                self.tender_id, qualifications[i]["id"], self.tender_token
            ),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, qualifications[-1]["id"], self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.set_status("active.pre-qualification.stand-still", "end")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TenderLotFeatureBidderResourceTest


def create_tender_feature_bidder(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.lot_id}]
    bid_data["parameters"] = [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0.01},
    ]
    del bid_data["value"]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    bidder = response.json["data"]
    self.assertEqual(bidder["tenderers"][0]["name"], self.initial_data["procuringEntity"]["name"])
    self.assertIn("id", bidder)
    self.assertIn(bidder["id"], response.headers["Location"])

    self.time_shift("active.pre-qualification")
    self.check_chronograph()

    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add bid in current (unsuccessful) tender status")


def create_tender_feature_bidder_invalid(self):
    request_path = "/tenders/{}/bids".format(self.tender_id)

    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    bid_data["lotValues"] = [{"value": {"amount": 500}}]
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
                u"description": [{u"relatedLot": [u"This field is required."]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": "0" * 32}]
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
                u"description": [{u"relatedLot": [u"relatedLot should be one of lots"]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    bid_data["lotValues"] = [{"value": {"amount": 5000000}, "relatedLot": self.lot_id}]
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
                u"description": [{u"value": [u"value of bid should be less than value of lot"]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    bid_data["lotValues"] = [{"value": {"amount": 500, "valueAddedTaxIncluded": False}, "relatedLot": self.lot_id}]
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
                u"description": [
                    {
                        u"value": [
                            u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot"
                        ]
                    }
                ],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    bid_data["lotValues"] = [{"value": {"amount": 500, "currency": "USD"}, "relatedLot": self.lot_id}]
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
                u"description": [{u"value": [u"currency of bid should be identical to currency of value of lot"]}],
                u"location": u"body",
                u"name": u"lotValues",
            }
        ],
    )

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.lot_id}]
    response = self.app.post_json(
        request_path,
        {"data": bid_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    bid_data["lotValues"] = [{"value": {"amount": 500}, "relatedLot": self.lot_id}]
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
        [{u"description": [u"All features parameters is required."], u"location": u"body", u"name": u"parameters"}],
    )

    bid_data["parameters"] = [{"code": "code_item", "value": 0.01}]
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
        [{u"description": [u"All features parameters is required."], u"location": u"body", u"name": u"parameters"}],
    )

    bid_data["parameters"] = [{"code": "code_invalid", "value": 0.01}]
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
                u"description": [{u"code": [u"code should be one of feature code."]}],
                u"location": u"body",
                u"name": u"parameters",
            }
        ],
    )

    bid_data["parameters"] = [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0},
    ]
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
                u"description": [{u"value": [u"value should be one of feature value."]}],
                u"location": u"body",
                u"name": u"parameters",
            }
        ],
    )
